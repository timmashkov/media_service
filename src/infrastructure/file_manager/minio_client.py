import logging
import os
from asyncio import AbstractEventLoop, get_event_loop
from datetime import datetime
from typing import AsyncGenerator, Iterator, Optional, Protocol, Union

import certifi
from minio import Minio, S3Error
from minio.commonconfig import Tags
from minio.helpers import MIN_PART_SIZE
from urllib3 import HTTPResponse, PoolManager, Retry, Timeout

from application.config import settings
from infrastructure.exceptions.minio_exceptions import OutDiskSpace
from infrastructure.handlers.asyncio_handler import run_in_executor


class FileReaderProtocol(Protocol):
    def read(self) -> bytes:
        pass


class MinioClient:
    def __init__(
        self,
        protocol: str,
        host: str,
        port: Union[str, int],
        access_key: str,
        secret_key: str,
        region: str,
        chunk_size: int = 1024,
        timeout=300,
        pool_max_size=30,
        cert_check=True,
        retry_count=5,
        loop: AbstractEventLoop = get_event_loop(),
        logger: logging.Logger = logging,
    ):
        self.chunk_size = chunk_size
        self.loop = loop
        self.logger = logger
        self.client = Minio(
            endpoint=f"{host}:{port}",
            secure=True if protocol == "https" else False,
            access_key=access_key,
            secret_key=secret_key,
            region=region,
            http_client=PoolManager(
                timeout=Timeout(connect=timeout, read=timeout),
                maxsize=pool_max_size,
                cert_reqs="CERT_REQUIRED" if cert_check else "CERT_NONE",
                ca_certs=os.environ.get("SSL_CERT_FILE") or certifi.where(),
                retries=Retry(
                    total=retry_count,
                    backoff_factor=0.2,
                    status_forcelist=[500, 502, 503, 504],
                ),
            ),
        )

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        mimetype: str,
        data: FileReaderProtocol,
        **kwargs,
    ) -> str:
        self.logger.warning(
            "Загрузка файла %s в bucket %s...", object_name, bucket_name
        )
        length = kwargs.pop("length", -1)
        kwargs["part_size"] = MIN_PART_SIZE if length == -1 else 0
        minio_tags = Tags(for_object=True)
        minio_tags.update(**kwargs.pop("tags", {}))
        try:
            response = await run_in_executor(
                loop=self.loop,
                func=self.client.put_object,
                bucket_name=bucket_name,
                object_name=self.format_masks(object_name, mimetype),
                data=data,
                length=length,
                tags=minio_tags,
                **kwargs,
            )
        except S3Error as error:
            if error.code == settings.S3_ERRORS.NO_SUCH_BUCKET:
                self.logger.warning("Не найден bucket %s...", bucket_name)
                await run_in_executor(
                    loop=self.loop,
                    func=self.client.make_bucket,
                    bucket_name=bucket_name,
                )
                self.logger.warning("Bucket %s успешно создан", bucket_name)
                return await self.upload_file(
                    bucket_name, object_name, mimetype, data, **kwargs
                )
            if error.code == settings.S3_ERRORS.MINIO_STORAGE_FULL:
                self.logger.error("Закончилось место на диске")
                raise OutDiskSpace("Закончилось место на диске")
            raise error
        self.logger.warning(
            "Загрузка файла %s в bucket %s прошла успешно", object_name, bucket_name
        )
        return response.object_name

    async def download_file_raw(
        self, bucket_name, object_name, **kwargs
    ) -> HTTPResponse:
        self.logger.debug("Загрузка файла %s из bucket %s...", object_name, bucket_name)
        response = await run_in_executor(
            loop=self.loop,
            func=self.client.get_object,
            bucket_name=bucket_name,
            object_name=object_name,
            **kwargs,
        )
        self.logger.debug(
            "Загрузка файла %s из bucket %s прошла успешно", object_name, bucket_name
        )
        return response

    async def download_file(self, bucket_name, object_name, **kwargs) -> bytes:
        response = None
        try:
            response = await self.download_file_raw(
                bucket_name=bucket_name, object_name=object_name, **kwargs
            )
            return response.data
        finally:
            if response:
                response.close()
                response.release_conn()

    async def download_file_chunk(
        self, bucket_name, object_name, **kwargs
    ) -> AsyncGenerator:
        response = None
        offset = 0
        try:
            while True:
                response = await self.download_file_raw(
                    bucket_name=bucket_name,
                    object_name=object_name,
                    length=self.chunk_size,
                    offset=offset,
                    **kwargs,
                )
                offset += self.chunk_size
                yield response.data
                if len(response.data) < self.chunk_size:
                    break
        finally:
            if response:
                response.close()
                response.release_conn()

    async def delete_object(self, bucket_name: str, object_name: str, **kwargs) -> None:
        await run_in_executor(
            loop=self.loop,
            func=self.client.remove_object,
            bucket_name=bucket_name,
            object_name=object_name,
            **kwargs,
        )

    async def get_list_objects(self, bucket_name: str, **kwargs) -> Iterator:
        return await run_in_executor(
            loop=self.loop,
            func=self.client.list_objects,
            bucket_name=bucket_name,
            **kwargs,
        )

    async def check_file_exist(
        self, bucket_name: str, object_name: str, **kwargs
    ) -> bool:
        try:
            await run_in_executor(
                loop=self.loop,
                func=self.client.stat_object,
                bucket_name=bucket_name,
                object_name=object_name,
                **kwargs,
            )
        except S3Error as error:
            if error.code in (
                settings.S3_ERRORS.NO_SUCH_FILE,
                settings.S3_ERRORS.NO_SUCH_BUCKET,
            ):
                return False
            raise error
        return True

    @classmethod
    def format_masks(
        cls, text: str, extension: str, date: Optional[datetime] = None
    ) -> str:
        type_ext = "." + extension.split("/")[-1]
        date = date or datetime.now()
        dates = {
            "DD": date.strftime("%d").zfill(2),
            "MM": date.strftime("%m").zfill(2),
            "YY": date.strftime("%y").zfill(2),
            "YYYY": date.strftime("%Y"),
            "MONTH": date.strftime("%B"),
        }
        return text.format(**dates) + type_ext
