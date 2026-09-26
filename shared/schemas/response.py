from typing import TypedDict


class Metadata(TypedDict):
    p: int
    rp: int
    total_data: int


class ErrorResponse(TypedDict):
    error: str
    errCode: str
