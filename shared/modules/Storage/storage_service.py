import os

from .storage import AWSStorage, Storage


class StorageService:
    def __new__(cls, bucket_name: str | None = None) -> Storage:

        return AWSStorage(bucket_name=(bucket_name or os.environ["S3_BUCKET"]))
