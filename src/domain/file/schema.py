import json
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, model_validator


class GetFileByUUID(BaseModel):
    uuid: UUID


class CreateFile(BaseModel):
    name: str
    path: str
    tags: Optional[dict]
    jdata: Optional[dict]
    references: Optional[str]
    reference_uuid: Optional[UUID]
    bucket: str
    mimetype: str = "image/jpg"

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return json.loads(value)
        return value


class FileReturnData(GetFileByUUID, CreateFile):
    created_at: datetime
    updated_at: datetime
