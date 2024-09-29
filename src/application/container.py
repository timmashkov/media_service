from redis.asyncio import Redis

from application.config import settings
from domain.file.registry import FileReadRegistry, FileWriteRegistry
from infrastructure.base_entities.singleton import OnlyContainer, Singleton
from infrastructure.database.alchemy_gateway import SessionManager
from infrastructure.file_manager.minio_client import MinioClient


class Container(Singleton):

    redis = OnlyContainer(
        Redis,
        **settings.REDIS,
        decode_responses=True,
    )

    alchemy_manager = OnlyContainer(
        SessionManager,
        dialect=settings.POSTGRES.dialect,
        host=settings.POSTGRES.host,
        login=settings.POSTGRES.login,
        password=settings.POSTGRES.password,
        port=settings.POSTGRES.port,
        database=settings.POSTGRES.database,
        echo=settings.POSTGRES.echo,
    )

    file_hosting_client = OnlyContainer(
        MinioClient,
        protocol=settings.S3.protocol,
        host=settings.S3.host,
        port=settings.S3.port,
        access_key=settings.S3.access_key,
        secret_key=settings.S3.secret_key,
        region=settings.S3.region,
        chunk_size=settings.S3.chunk_size,
        loop=None,
    )

    file_read_registry = OnlyContainer(
        FileReadRegistry,
        session_manager=alchemy_manager(),
    )

    file_write_registry = OnlyContainer(
        FileWriteRegistry,
        session_manager=alchemy_manager(),
    )
