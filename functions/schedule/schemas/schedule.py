from typing import NotRequired, TypedDict

from functions.documents.schemas.document import DocumentMetadataRow


class ScheduleRow(TypedDict):
    id: str
    serial_number: int
    name: str
    phone_number: str
    email: str


class GetSchedulesResult(TypedDict):
    schedules: list[ScheduleRow]
    total_data: int


class DetailScheduleRow(TypedDict):
    id: str
    course_id: str
    start_date: str
    end_date: str
    location: str
    course_mode_id: str
    serial_number: int


class GetDetailScheduleResult(TypedDict):
    schedule: DetailScheduleRow
    documents: list[DocumentMetadataRow]


class CreateScheduleResult(TypedDict):
    schedule: DetailScheduleRow


class ScheduleOwnerRow(TypedDict):
    id: str
