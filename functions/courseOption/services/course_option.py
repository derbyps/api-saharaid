from ..repositories.course_certificate_validity import (
    CourseCertificateValidityRepository,
)
from ..repositories.course_class_type import CourseClassTypeRepository
from ..repositories.course_type import CourseTypeRepository
from ..schemas.event import GetParams
from ..schemas.response import CourseOptionResponse


class CourseOptionService:
    def __init__(self):
        self.type_repo = CourseTypeRepository()
        self.class_type_repo = CourseClassTypeRepository()
        self.certificate_validity = CourseCertificateValidityRepository()

    def get(self, params: GetParams) -> CourseOptionResponse:
        include = params.get("include")
        response: CourseOptionResponse = {}

        if include and "type" in include:
            type = self.type_repo.get_type()
            response["type"] = type

        if include and "class_type" in include:
            class_type = self.class_type_repo.get_class_type()
            response["class_type"] = class_type

        if include and "certificate_validity" in include:
            certificate_validity = self.certificate_validity.get_certificate_validity()
            response["certificate_validity"] = certificate_validity

        return response
