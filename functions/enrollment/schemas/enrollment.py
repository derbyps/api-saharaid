from typing import TypedDict


class EnrollmentRow(TypedDict):
    id: str
    course_id: str
    schedule_id: str
    participant_name: str
    course_name: str
    start_date: str
    end_date: str
    enroll_date: str
    serial_number: int


class GetEnrollmentsResult(TypedDict):
    enrollments: list[EnrollmentRow]
    total_data: int


class CreateEnrollmentResult(TypedDict):
    inserted: int
