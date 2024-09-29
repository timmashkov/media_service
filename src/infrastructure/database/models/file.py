import uuid

from sqlalchemy import UUID, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.database.models.base import Base


class File(Base):
    name: Mapped[str] = mapped_column(Text, nullable=False, comment="Название")
    references: Mapped[str] = mapped_column(
        Text, index=True, nullable=True, comment="Связанный объект"
    )
    reference_uuid: Mapped[uuid.UUID] = mapped_column(
        UUID, index=True, nullable=True, comment="Идентификатор связанного объекта"
    )
    bucket: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Bucket хранилища"
    )
    path: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Путь к файлу в bucket"
    )
    mimetype: Mapped[str] = mapped_column(
        Text, nullable=False, comment="Тип файла по спецификации MIME"
    )
    jdata: Mapped[dict] = mapped_column(
        JSONB, nullable=True, server_default="{}", comment="Доп данные"
    )  # noqa: P103
    tags: Mapped[dict] = mapped_column(
        JSONB, nullable=True, server_default="{}", comment="Теги"
    )  # noqa: P103
