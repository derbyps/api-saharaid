import os
import re
from io import BytesIO
from typing import Any
from urllib.parse import quote, unquote

import boto3


class S3Manager:
    def __init__(self, bucket_name: str | None = None) -> None:
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name

    def get_file_bytes(self, s3_file_key: str) -> tuple[bytes, str] | None:
        try:
            response = self.s3_client.get_object(
                Bucket=self.bucket_name or os.environ["S3_BUCKET"], Key=s3_file_key
            )

            return response["Body"].read(), response["ContentType"]

        except:
            return None

    def list_objects_v2(self, prefix: str) -> list:

        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name or os.environ["S3_BUCKET"],
                Prefix=prefix,
            )

            return response.get("Contents") or []

        except:
            return []

    def download_fileobj(self, s3_file_key: str, fileobj: BytesIO):
        self.s3_client.download_fileobj(
            Bucket=self.bucket_name or os.environ["S3_BUCKET"],
            Key=s3_file_key,
            Fileobj=fileobj,
        )

    def upload_fileobj(
        self, fileobj: BytesIO, s3_key: str, extra_args: dict[str, Any] | None = None
    ) -> None:
        fileobj.seek(0)

        self.s3_client.upload_fileobj(
            Fileobj=fileobj,
            Bucket=self.bucket_name or os.environ["S3_BUCKET"],
            Key=s3_key,
            ExtraArgs=extra_args,
        )

    def generate_presigned_url(
        self,
        s3_key: str,
        expires_in: int = 900,
    ) -> str:
        return self.s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": self.bucket_name or os.environ["S3_BUCKET"],
                "Key": s3_key,
            },
            ExpiresIn=expires_in,
        )

    def make_content_disposition(self, filename: str) -> str:
        encoded = quote(unquote(filename), safe="")

        return f"attachment; filename*=UTF-8''{encoded}"

    def url_safe(self, filename: str) -> str:
        return re.sub(r"[/\\]", "-", filename)


# SINGLETON
_s3_manager: S3Manager | None = None


def init_s3_manager(*, bucket_name: str) -> None:
    """
    Initialize the singleton S3Manager.
    Must be called exactly once (e.g. in lambda_handler).
    """
    global _s3_manager
    if _s3_manager is not None:
        return

    _s3_manager = S3Manager(bucket_name=bucket_name)


def s3_manager() -> S3Manager:
    if _s3_manager is None:
        raise RuntimeError("S3Manager is not initialized.")

    return _s3_manager
