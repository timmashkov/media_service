from typing import List, Optional

from fastapi import Depends

from application.container import Container
from domain.file.registry import FileReadRegistry, FileWriteRegistry
from domain.file.schema import CreateFile, FileReturnData, GetFileByUUID
from infrastructure.file_manager.minio_client import MinioClient


class FileService:
    def __init__(
        self,
        file_read: FileReadRegistry = Depends(Container.file_read_registry),
        file_write: FileWriteRegistry = Depends(Container.file_write_registry),
        minio: MinioClient = Depends(Container.file_hosting_client),
    ) -> None:
        self.read_repo = file_read
        self.write_repo = file_write
        self.file_manager = minio

    async def get(self, cmd: GetFileByUUID) -> Optional[FileReturnData]:
        return await self.read_repo.get(file_uuid=cmd.uuid)

    async def get_list(self, parameter: str) -> Optional[List[FileReturnData]]:
        return await self.read_repo.get_list(parameter=parameter)

    async def create(self, file: CreateFile, file_data) -> Optional[FileReturnData]:
        await self.file_manager.upload_file(
            bucket_name=file.bucket,
            object_name=file.path,
            data=file_data,
            tags=file.tags,
        )
        return await self.write_repo.create(cmd=file)

    async def update(
        self, data: CreateFile, file_uuid: GetFileByUUID
    ) -> Optional[FileReturnData]:
        return await self.write_repo.update(cmd=data, file_uuid=file_uuid.uuid)

    async def delete(self, file_uuid: GetFileByUUID) -> Optional[FileReturnData]:
        return await self.write_repo.delete(file_uuid=file_uuid.uuid)
