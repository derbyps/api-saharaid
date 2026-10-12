from typing import TypedDict

from functions.documents.schemas.document import DocumentMetadataRow


class ScheduleRow(TypedDict):
    id: str
    serial_number: int
    course_name: str
    batch: str
    class_type: str | None
    location: str
    start_date: str
    end_date: str
    participant_count: int
    created_at: str


class GetSchedulesResult(TypedDict):
    schedules: list[ScheduleRow]
    total_data: int


class DetailScheduleRow(TypedDict):
    id: str
    course_id: str
    course_class_type_id: str
    start_date: str
    end_date: str
    location: str
    serial_number: int
    batch: str


class GetDetailScheduleResult(TypedDict):
    schedule: DetailScheduleRow
    documents: list[DocumentMetadataRow]


class CreateScheduleResult(TypedDict):
    schedule: DetailScheduleRow


class ScheduleOwnerRow(TypedDict):
    id: str
