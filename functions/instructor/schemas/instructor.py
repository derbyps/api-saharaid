from typing import NotRequired, TypedDict

from ..schemas.document import DocumentsRow


class InstructorRow(TypedDict):
    id: str
    name: str
    phone_number: str
    email: str
    course_theme_id: str
    specialization: str
    created_at: str
    created_by: str
    passport_photo: str | None
    cv: str | None
    course_theme_name: str


class GetInstructorsResult(TypedDict):
    instructors: list[InstructorRow]
    total_data: int


class DetailInstructorRow(TypedDict):
    id: str
    name: str
    phone_number: str
    email: str
    course_theme_id: str
    specialization: str
    created_at: str
    created_by: NotRequired[str]
    course_theme_name: str


class GetDetailInstructorResult(TypedDict):
    instructor: DetailInstructorRow
    documents: list[DocumentsRow]
