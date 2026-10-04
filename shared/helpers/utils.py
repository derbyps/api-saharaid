import math
import os
import traceback
from datetime import timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import TYPE_CHECKING, Literal, Optional, Union, overload

from botocore.exceptions import NoCredentialsError

from ..repositories.types import ROUNDING_TYPES

if TYPE_CHECKING:
    from mypy_boto3_s3.client import S3Client


def get_s3_signed_url(
    s3_client: "S3Client",
    object_key: str,
    ttl: timedelta,
) -> str | None:
    print("ssss", os.getenv("S3_BUCKET"))
    try:
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": os.getenv("S3_BUCKET"),
                "Key": object_key,
            },
            ExpiresIn=int(ttl.total_seconds()),
        )

        return url

    except NoCredentialsError:
        traceback.print_exc()
        return None


@overload
def convert_int(
    n,
    allow_null: Literal[True],
    round_to: ROUNDING_TYPES = ...,
    decimal_place: int = ...,
) -> Union[int, None]: ...


@overload
def convert_int(
    n,
    allow_null: Literal[False] = ...,
    round_to: ROUNDING_TYPES = ...,
    decimal_place: int = ...,
) -> int: ...


def convert_int(
    n,
    allow_null: bool = False,
    round_to: ROUNDING_TYPES = "nearest",
    decimal_place: int = 0,
) -> Optional[Union[int, float]]:
    if n is None and allow_null:
        return None

    try:
        if decimal_place:
            factor = Decimal("1." + "0" * decimal_place)
            res = Decimal(n).quantize(factor, rounding=ROUND_HALF_UP)

            return float(res)

        if round_to == "down":
            return math.floor(n)

        if round_to == "up":
            return math.ceil(n)

        res = Decimal(n).to_integral_value(rounding=ROUND_HALF_UP)

    except Exception:
        res = 0

    return int(res)


@overload
def convert_float(n, allow_null: Literal[True]) -> Union[float, None]: ...


@overload
def convert_float(n, allow_null: Literal[False] = ...) -> float: ...


def convert_float(n, allow_null: bool = False) -> Union[float, None]:
    if n is None and allow_null:
        return None

    try:
        res = float(n)

    except Exception:
        res = 0

    return res


def convert_str(s, allow_null: bool = True) -> Union[str, None]:
    if s is None and allow_null:
        return None

    try:
        res = str(s)

    except:
        res = ""

    return res
