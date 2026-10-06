from typing import NotRequired, TypedDict

from shared.models.course_certificate_validity import CourseCertificateValidity
from shared.models.course_class_type import CourseClassType
from shared.models.course_type import CourseType


class CourseOptionResponse(TypedDict):
    type: NotRequired[list[CourseType]]
    class_type: NotRequired[list[CourseClassType]]
    certificate_validity: NotRequired[list[CourseCertificateValidity]]
