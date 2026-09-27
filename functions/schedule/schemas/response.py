from typing import TypedDict

from functions.documents.schemas.document import DocumentMetadataRow
from shared.schemas.response import Metadata

from .schedule import DetailScheduleRow


class PaginatedSchedulesResponse(TypedDict):
    schedules: list
    metadata: Metadata


class CreateScheduleResponse(TypedDict):
    schedule: DetailScheduleRow


class GetDetailScheduleResponse(TypedDict):
    schedule: DetailScheduleRow
