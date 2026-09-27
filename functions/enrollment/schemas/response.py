from typing import TypedDict

from shared.schemas.response import Metadata

from .enrollment import DetailEnrollmentRow


class PaginatedEnrollmentsResponse(TypedDict):
    enrollments: list
    metadata: Metadata


class CreateEnrollmentResponse(TypedDict):
    enrollment: DetailEnrollmentRow
