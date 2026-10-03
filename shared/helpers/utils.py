import os
import traceback
from datetime import timedelta

from botocore.exceptions import NoCredentialsError
from mypy_boto3_s3.client import S3Client


def get_s3_signed_url(
    s3_client: S3Client, object_key: str, ttl: timedelta
) -> str | None:
    try:
        # Generate the presigned URL for getting the object
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": os.getenv("S3_RESOURCES_BUCKET"), "Key": object_key},
            ExpiresIn=int(ttl.total_seconds()),
        )

        return url
    except NoCredentialsError:
        traceback.print_exc()
        return None
