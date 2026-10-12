from typing import TypedDict


class CourseResult(TypedDict):
    id: str
    sanity_id: str
    title: str
    asset_status: str


class PresignCourseResult(TypedDict):
    files: list[dict[str, str]]
    expires_in: int
