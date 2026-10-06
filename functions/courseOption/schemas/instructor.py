from typing import NotRequired, TypedDict


class DetailInstructorRow(TypedDict):
    id: str
    name: str
    phone_number: str
    email: str
    course_theme_id: str
    specialization: str
    created_at: str
    created_by: NotRequired[str]
