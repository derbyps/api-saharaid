from typing import TypedDict


class DocumentsRow(TypedDict):
    id: str
    owner_id: str
    owner_type: str
    document_type: str
    s3_key: str | None
    content_type: str
    course_theme_name: str
