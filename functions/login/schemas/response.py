from typing import Literal, TypedDict

from .login import LoginUserRow


class LoginSuccessResponse(TypedDict):
    user: LoginUserRow
    token: str
    refreshToken: str


class LoginChallengeResponse(TypedDict):
    challenge: Literal["NEW_PASSWORD_REQUIRED"]
    email: str
    session: str
