from typing import TypedDict

from .course import CourseResult


class CourseResponse(TypedDict):
    course: CourseResult
