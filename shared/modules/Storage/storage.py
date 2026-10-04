from abc import ABC, abstractmethod
from io import BytesIO

from ...constant.file import FileContentTypes as file
from ...constant.storage import StorageFolder
from ...modules.AWSManager.aws_s3 import S3Manager
from ...modules.Generator.uuid import uuid7


class Storage(ABC):
    @abstractmethod
    def upload_excel(self, data: bytes, folder: StorageFolder, filename: str) -> str:
        """Upload excel and return a accessible/presigned URL"""
        ...

    @abstractmethod
    def upload_xml(self, data: str, folder: StorageFolder, filename: str) -> str:
        """Upload excel and return a accessible/presigned URL"""
        ...


class AWSStorage(Storage):
    def __init__(self, bucket_name: str):
        self.s3 = S3Manager(bucket_name)

    def upload_excel(self, data: bytes, folder: StorageFolder, filename: str) -> str:

        s3_key = f"{folder}/{filename}/{uuid7()}.xlsx"

        if not filename.endswith(".xlsx"):
            filename += ".xlsx"

        self.s3.upload_fileobj(
            fileobj=BytesIO(data),
            s3_key=s3_key,
            extra_args={
                "ContentType": file.EXCEL,
                "ContentDisposition": self.s3.make_content_disposition(filename),
            },
        )

        return self.s3.generate_presigned_url(s3_key)

    def upload_xml(self, data: str, folder: StorageFolder, filename: str) -> str:

        s3_key = f"{folder}/{filename}/{uuid7()}.xml"

        if not filename.endswith(".xml"):
            filename += ".xml"

        self.s3.upload_fileobj(
            fileobj=BytesIO(data.encode("utf-8")),
            s3_key=s3_key,
            extra_args={
                "ContentType": file.XML,
                "ContentDisposition": self.s3.make_content_disposition(filename),
            },
        )

        return self.s3.generate_presigned_url(s3_key)
