from typing import TypedDict

from shared.schemas.response import Metadata


class PaginatedEnrollmentsResponse(TypedDict):
    enrollments: list
    metadata: Metadata


class CreateEnrollmentResponse(TypedDict):
    inserted: int
