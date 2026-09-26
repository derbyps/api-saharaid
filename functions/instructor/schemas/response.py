from typing import TypedDict

from shared.schemas.response import Metadata


class PaginatedInstructorsResponse(TypedDict):
    instructors: list
    metadata: Metadata
