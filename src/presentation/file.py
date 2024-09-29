from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from pydantic import BaseModel

from domain.file.schema import CreateFile, FileReturnData, GetFileByUUID
from service.file import FileService


class FileRouter:
    api_router = APIRouter(prefix="/file", tags=["File"])
    output_model: BaseModel = FileReturnData
    input_model: BaseModel = CreateFile
    service_client: FileService = Depends(FileService)

    @staticmethod
    @api_router.get("/one", response_model=output_model)
    async def get(
        file_uuid: str | UUID,
        service=service_client,
    ) -> output_model:
        return await service.get(cmd=GetFileByUUID(uuid=file_uuid))

    @staticmethod
    @api_router.get("/all", response_model=List[output_model])
    async def get_list(
        parameter: str = "created_at",
        service=service_client,
    ) -> List[output_model]:
        return await service.get_list(parameter=parameter)

    @staticmethod
    @api_router.post("/create", response_model=output_model)
    async def create(
        incoming_data: input_model,
        data: UploadFile,
        service=service_client,
    ) -> output_model:
        return await service.create(file=incoming_data, file_data=data.file)

    @staticmethod
    @api_router.patch("/update{user_uuid}", response_model=output_model)
    async def update(
        file_uuid: str | UUID,
        incoming_data: input_model,
        service=service_client,
    ) -> output_model:
        return await service.update(
            data=incoming_data, file_uuid=GetFileByUUID(uuid=file_uuid)
        )

    @staticmethod
    @api_router.delete("/delete", response_model=output_model)
    async def delete(
        file_uuid: str | UUID,
        service=service_client,
    ) -> output_model:
        return await service.delete(file_uuid=GetFileByUUID(uuid=file_uuid))
