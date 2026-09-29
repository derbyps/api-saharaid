from shared import util

from ..schemas.event import LoginBody
from ..schemas.response import LoginChallengeResponse, LoginSuccessResponse
from ..services.login import LoginService


def login_handler(event: dict) -> dict:
    body = util.parse_body(event)
    email, password = body.get("email"), body.get("password")
    if (
        not isinstance(email, str)
        or not email.strip()
        or not isinstance(password, str)
        or not password
    ):
        raise util.HttpError(400, "INVALID_BODY", "email and password are required")

    credentials: LoginBody = {"email": email.strip(), "password": password}

    result = LoginService().login(credentials)

    if result["kind"] == "challenge":
        response: LoginChallengeResponse = {
            "challenge": "NEW_PASSWORD_REQUIRED",
            "email": result["email"],
            "session": result["session"],
        }
    else:
        response: LoginSuccessResponse = {
            "user": result["user"],
            "token": result["token"],
            "refreshToken": result["refresh_token"],
        }

    return util.return_response(200, dict(response))
