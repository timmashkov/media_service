from typing import Any, List, Optional
from uuid import UUID

from asyncpg import UniqueViolationError
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker

from domain.file.schema import CreateFile
from infrastructure.base_entities.abs_repository import (
    AbstractReadRepository,
    AbstractWriteRepository,
)
from infrastructure.database.alchemy_gateway import SessionManager
from infrastructure.database.models import File
from infrastructure.exceptions.minio_exceptions import FileAlreadyExist


class FileReadRegistry(AbstractReadRepository):
    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.model = File
        self.transactional_session: async_sessionmaker = (
            session_manager.transactional_session
        )
        self.async_session_factory: async_sessionmaker = (
            session_manager.async_session_factory
        )

    async def get(self, file_uuid: UUID) -> Optional[File]:
        async with self.transactional_session() as session:
            stmt = select(self.model).filter(self.model.uuid == file_uuid)
            result = await session.execute(stmt)
            answer = result.scalar_one_or_none()
        return answer

    async def get_list(
        self,
        parameter: Any = "created_at",
    ) -> Optional[List[File]]:
        async with self.async_session_factory() as session:
            final = None
            if option := getattr(self.model, parameter):
                stmt = select(self.model).order_by(option)
                result = await session.execute(stmt)
                final = result.scalars().all()
        return final


class FileWriteRegistry(AbstractWriteRepository):
    def __init__(self, session_manager: SessionManager):
        super().__init__()
        self.model = File
        self.transactional_session: async_sessionmaker = (
            session_manager.transactional_session
        )
        self.async_session_factory: async_sessionmaker = (
            session_manager.async_session_factory
        )

    async def create(self, cmd: CreateFile) -> Optional[File]:
        try:
            async with self.transactional_session() as session:
                stmt = (
                    insert(self.model).values(**cmd.model_dump()).returning(self.model)
                )
                result = await session.execute(stmt)
                await session.commit()
                answer = result.scalar_one_or_none()
            return answer
        except (UniqueViolationError, IntegrityError):
            raise FileAlreadyExist

    async def update(
        self,
        cmd: CreateFile,
        file_uuid: UUID,
    ) -> Optional[File]:
        async with self.transactional_session() as session:
            stmt = (
                update(self.model)
                .values(**cmd.model_dump())
                .where(self.model.uuid == file_uuid)
                .returning(self.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            answer = result.scalar_one_or_none()
        return answer

    async def delete(self, file_uuid: UUID) -> Optional[File]:
        async with self.transactional_session() as session:
            stmt = (
                delete(self.model)
                .where(self.model.uuid == file_uuid)
                .returning(self.model)
            )
            result = await session.execute(stmt)
            await session.commit()
            answer = result.scalar_one_or_none()
        return answer
