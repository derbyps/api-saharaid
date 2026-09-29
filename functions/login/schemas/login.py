from typing import Literal, TypedDict


class LoginUserRow(TypedDict):
    id: str
    name: str
    email: str


class LoginSuccessResult(TypedDict):
    kind: Literal["success"]
    user: LoginUserRow
    token: str
    refresh_token: str


class LoginChallengeResult(TypedDict):
    kind: Literal["challenge"]
    email: str
    session: str
