from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from infrastructure.database.models import File


class GetFileByUUID(BaseModel):
    uuid: UUID


class CreateFile(BaseModel):
    name: str = Field(description=File.name.comment)
    path: str = Field(description=File.path.comment)
    tags: Optional[dict] = Field(default=None, description=File.tags.comment)
    jdata: Optional[dict] = Field(default=None, description=File.jdata.comment)
    references: Optional[str] = Field(default=None, description=File.references.comment)
    reference_uuid: Optional[UUID] = Field(default=None, description=File.reference_uuid.comment)
    bucket: str = Field(description=File.bucket.comment)
    mimetype: str = Field(description=File.mimetype.comment)


class FileReturnData(GetFileByUUID, CreateFile):
    created_at: datetime
    updated_at: datetime
