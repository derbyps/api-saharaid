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


class CognitoManager:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.client = boto3.client("cognito-idp")

    def login(self, email: str, password: str) -> dict:
        return self.client.initiate_auth(
            ClientId=self.client_id,
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": email, "PASSWORD": password},
        )

    def email_for_token(self, access_token: str) -> str:
        attributes = self.client.get_user(AccessToken=access_token)["UserAttributes"]
        return next((item["Value"] for item in attributes if item["Name"] == "email"), "")
