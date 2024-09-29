from fastapi import status

from infrastructure.base_entities.base_exception import BaseAPIException


class OutDiskSpace(BaseAPIException):
    message = "Minio storage is full"
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE


class FileNotFound(BaseAPIException):
    message = "File not found"
    status_code = status.HTTP_404_NOT_FOUND


class FileAlreadyExist(BaseAPIException):
    message = "File already exist"
    status_code = status.HTTP_400_BAD_REQUEST
