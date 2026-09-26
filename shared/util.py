import json
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from functools import lru_cache
from typing import Any, TypeVar, overload
from uuid import UUID
from zoneinfo import ZoneInfo

from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy import func, select
from sqlalchemy.engine.row import Row

from shared.configs.db import db
from shared.models.user import User

T = TypeVar("T", bound=Mapping[str, Any])

JAKARTA = ZoneInfo("Asia/Jakarta")


class HttpError(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code


def _json_default(value):
    if isinstance(value, datetime):
        return value.astimezone(JAKARTA).isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def return_response(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"content-type": "application/json"},
        "body": json.dumps(data, default=_json_default),
    }


def parse_body(event: dict) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except (TypeError, ValueError) as exc:
        raise HttpError(400, "INVALID_BODY", "Request body must be valid JSON") from exc
    if not isinstance(body, dict):
        raise HttpError(400, "INVALID_BODY", "Request body must be a JSON object")
    return body


@lru_cache(maxsize=1)
def _cognito():
    import boto3

    return boto3.client("cognito-idp")


def current_user_id(event: dict) -> UUID:
    claims = (
        event.get("requestContext", {})
        .get("authorizer", {})
        .get("jwt", {})
        .get("claims", {})
    )
    if claims.get("token_use") != "access":
        raise HttpError(401, "UNAUTHORIZED", "A Cognito access token is required")

    headers = {key.lower(): value for key, value in event.get("headers", {}).items()}
    authorization = headers.get("authorization", "")
    if not authorization.lower().startswith("bearer "):
        raise HttpError(401, "UNAUTHORIZED", "A Cognito access token is required")
    token = authorization[7:].strip()
    if not token:
        raise HttpError(401, "UNAUTHORIZED", "A Cognito access token is required")

    try:
        attributes = _cognito().get_user(AccessToken=token)["UserAttributes"]
    except ClientError as exc:
        if exc.response.get("Error", {}).get("Code") == "NotAuthorizedException":
            raise HttpError(401, "UNAUTHORIZED", "Invalid access token") from exc
        raise HttpError(
            502, "COGNITO_UNAVAILABLE", "Cognito user lookup failed"
        ) from exc
    except BotoCoreError as exc:
        raise HttpError(
            502, "COGNITO_UNAVAILABLE", "Cognito user lookup failed"
        ) from exc

    email = next((item["Value"] for item in attributes if item["Name"] == "email"), "")
    if not email:
        raise HttpError(403, "USER_NOT_FOUND", "Backoffice user not found")
    user_id = db.session.scalar(
        select(User.id).where(
            func.lower(func.trim(User.email)) == email.strip().lower()
        )
    )
    if user_id is None:
        raise HttpError(403, "USER_NOT_FOUND", "Backoffice user not found")
    return user_id


@overload
def serialize(datas: Row, typeddict_class: type[T]) -> T: ...


@overload
def serialize(datas: None, typeddict_class: type[T]) -> None: ...


@overload
def serialize(datas: Sequence[Row], typeddict_class: type[T]) -> list[T]: ...


def serialize(
    datas: Sequence | Row | None, typeddict_class: type[T]
) -> None | T | list[T]:
    if datas is None:
        return None

    columns = typeddict_class.__annotations__.keys()

    def get_attr(data, column):

        if getattr(data, column, None) is None:
            return None

        if typeddict_class.__annotations__[column] == int:
            try:
                res = int(getattr(data, column, 0))
            except:
                res = 0

            return res

        if typeddict_class.__annotations__[column] == str:
            try:
                res = str(getattr(data, column, ""))
            except:
                res = ""

            return res

        if typeddict_class.__annotations__[column] == (str | None):
            try:
                res = str(getattr(data, column, None))
            except:
                res = None

            return res

        if typeddict_class.__annotations__[column] == float:
            try:
                res = float(getattr(data, column, 0.0))
            except:
                res = 0.0

            return res

        if typeddict_class.__annotations__[column] == bool:
            try:
                res = bool(getattr(data, column, False))
            except:
                res = False

            return res

        return getattr(data, column, None)

    if not isinstance(datas, Row):
        res = []
        for data in datas:
            res.append(
                typeddict_class({column: get_attr(data, column) for column in columns})  # type: ignore
            )

        return res

    else:
        # Extract the values from the query result based on column names
        values = {column: get_attr(datas, column) for column in columns}

        # Instantiate the TypedDict with the extracted values
        serialized_data = typeddict_class(values)  # type: ignore

        return serialized_data
        return serialized_data
