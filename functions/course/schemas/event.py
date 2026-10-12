from typing import NotRequired, TypedDict


class CoursePayload(TypedDict):
    title: str
    slug: str
    theme_sanity_ids: list[str]
    course_type_id: str
    course_class_type_id: str
    course_certificate_validity_id: str
    duration: str
    overview: list[dict]
    objective: list[dict]
    outline: list[dict]
    requirement: list[dict]
    related_course_ids: list[str]
    recommended_for: list[str]
    has_assets: bool


class PresignFile(TypedDict):
    kind: str
    content_type: str


class PresignBody(TypedDict):
    files: list[PresignFile]


class GalleryItem(TypedDict):
    key: NotRequired[str]
    s3_key: NotRequired[str]


class BrochureItem(TypedDict):
    s3_key: str


class FinalizeBody(TypedDict):
    gallery: NotRequired[list[GalleryItem]]
    brochure: NotRequired[BrochureItem | None]
