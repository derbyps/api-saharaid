import json
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from botocore.exceptions import ClientError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from functions.login.lambda_function import lambda_handler
from shared.AWSManager import CognitoManager
from shared.configs.db import Base
from shared.models.user import User


class LoginTest(unittest.TestCase):
    def test_cognito_login_uses_password_flow_without_secret(self):
        with patch("shared.AWSManager.boto3.client") as client_factory:
            CognitoManager("client").login("admin@example.com", "password")
        client_factory.return_value.initiate_auth.assert_called_once_with(
            ClientId="client", AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": "admin@example.com", "PASSWORD": "password"},
        )

    def test_login_checks_database_before_cognito_and_handles_results(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        sessions = sessionmaker(engine)
        user_id = uuid4()
        with sessions.begin() as session:
            session.add(User(id=str(user_id), name="Admin", email="Admin@example.com"))

        cognito = Mock()
        cognito.email_for_token.return_value = "admin@example.com"

        def request(email, password="password"):
            response = lambda_handler({
                "rawPath": "/login",
                "requestContext": {"http": {"method": "POST"}},
                "body": json.dumps({"email": email, "password": password}),
            }, None)
            return response["statusCode"], json.loads(response["body"])

        with patch("shared.configs.db._session_factory", return_value=sessions), \
             patch("functions.login.services.login.CognitoManager", return_value=cognito), \
             patch.dict("os.environ", {"COGNITO_USER_POOL_ID": "pool", "COGNITO_APP_CLIENT_ID": "client"}):
            status, body = request("missing@example.com")
            self.assertEqual((status, body["errCode"]), (401, "INVALID_CREDENTIALS"))
            cognito.login.assert_not_called()

            cognito.login.return_value = {"AuthenticationResult": {"AccessToken": "access", "RefreshToken": "refresh"}}
            status, body = request(" admin@example.com ")
            self.assertEqual((status, body), (200, {
                "user": {"id": str(user_id), "name": "Admin", "email": "Admin@example.com"},
                "token": "access", "refreshToken": "refresh",
            }))
            cognito.login.assert_called_with("admin@example.com", "password")
            cognito.email_for_token.assert_called_with("access")

            cognito.login.return_value = {"ChallengeName": "NEW_PASSWORD_REQUIRED", "Session": "opaque"}
            self.assertEqual(request("admin@example.com"), (200, {
                "challenge": "NEW_PASSWORD_REQUIRED", "email": "admin@example.com", "session": "opaque",
            }))

            cognito.login.side_effect = ClientError({"Error": {"Code": "NotAuthorizedException"}}, "AdminInitiateAuth")
            status, body = request("admin@example.com")
            self.assertEqual((status, body["errCode"]), (401, "INVALID_CREDENTIALS"))

            cognito.login.side_effect = None
            cognito.login.return_value = {"AuthenticationResult": {"AccessToken": "access", "RefreshToken": "refresh"}}
            cognito.email_for_token.return_value = "different@example.com"
            status, body = request("admin@example.com")
            self.assertEqual((status, body["errCode"]), (403, "USER_NOT_FOUND"))


if __name__ == "__main__":
    unittest.main()
