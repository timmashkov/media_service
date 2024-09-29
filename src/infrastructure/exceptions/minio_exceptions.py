from fastapi import status

from infrastructure.base_entities.base_exception import BaseAPIException


class OutDiskSpace(BaseAPIException):
    message = "Minio storage is full"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
