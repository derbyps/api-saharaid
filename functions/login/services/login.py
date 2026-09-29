import os

from botocore.exceptions import BotoCoreError, ClientError

from shared import util
from shared.AWSManager import CognitoManager

from ..repositories.login import LoginRepository
from ..schemas.event import LoginBody
from ..schemas.login import LoginChallengeResult, LoginSuccessResult


class LoginService:
    def __init__(self):
        self.repo = LoginRepository()

    def login(
        self, credentials: LoginBody
    ) -> LoginSuccessResult | LoginChallengeResult:
        user = self.repo.get_user_by_email(credentials["email"])
        if user is None:
            raise util.HttpError(
                401, "INVALID_CREDENTIALS", "Invalid email or password"
            )

        cognito = CognitoManager(os.environ["COGNITO_APP_CLIENT_ID"])
        try:
            auth = cognito.login(credentials["email"], credentials["password"])

            if auth.get("ChallengeName") == "NEW_PASSWORD_REQUIRED":
                return {
                    "kind": "challenge",
                    "email": credentials["email"],
                    "session": auth["Session"],
                }

            if "ChallengeName" in auth:
                raise util.HttpError(
                    401,
                    "AUTH_CHALLENGE_UNSUPPORTED",
                    "Authentication challenge is not supported",
                )

            tokens = auth["AuthenticationResult"]

            if (
                cognito.email_for_token(tokens["AccessToken"]).strip().lower()
                != user["email"].strip().lower()
            ):
                raise util.HttpError(403, "USER_NOT_FOUND", "Backoffice user not found")

        except ClientError as exc:
            if exc.response.get("Error", {}).get("Code") in {
                "NotAuthorizedException",
                "UserNotFoundException",
                "PasswordResetRequiredException",
            }:
                raise util.HttpError(
                    401, "INVALID_CREDENTIALS", "Invalid email or password"
                ) from exc

            raise util.HttpError(
                502, "COGNITO_UNAVAILABLE", "Cognito login failed"
            ) from exc

        except BotoCoreError as exc:
            raise util.HttpError(
                502, "COGNITO_UNAVAILABLE", "Cognito login failed"
            ) from exc

        return {
            "kind": "success",
            "user": user,
            "token": tokens["AccessToken"],
            "refresh_token": tokens["RefreshToken"],
        }
