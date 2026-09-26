import boto3


class S3Manager:
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.client = boto3.client("s3")

    def generate_presigned_url(self, ClientMethod, Params=None, ExpiresIn=3600, HttpMethod=None):
        return self.client.generate_presigned_url(
            ClientMethod,
            Params={**(Params or {}), "Bucket": self.bucket},
            ExpiresIn=ExpiresIn,
            HttpMethod=HttpMethod,
        )

    def head_object(self, **kwargs):
        return self.client.head_object(Bucket=self.bucket, **kwargs)

    def delete_object(self, **kwargs):
        return self.client.delete_object(Bucket=self.bucket, **kwargs)
