from typing import NotRequired, TypedDict


class InstructorRow(TypedDict):
    id: str
    name: str
    phone_number: str
    email: str
    course_theme_id: str
    specialization: str
    created_at: str
    created_by: str


class GetInstructorsResult(TypedDict):
    instructors: list[InstructorRow]
    total_data: int


class DocumentsRow(TypedDict):
    id: str
    document_type: str
    original_filename: str
    content_type: str
    file_size: int
    last_modified_at: str
    uploaded_at: str


class DetailInstructorRow(TypedDict):
    id: str
    name: str
    phone_number: str
    email: str
    course_theme_id: str
    specialization: str
    created_at: str
    created_by: NotRequired[str]


class GetDetailInstructorResult(TypedDict):
    instructor: DetailInstructorRow
    documents: list[DocumentsRow]
