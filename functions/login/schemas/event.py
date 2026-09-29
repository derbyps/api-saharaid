from typing import TypedDict


class LoginBody(TypedDict):
    email: str
    password: str
