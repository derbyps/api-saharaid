from shared.configs import config as config_module
from shared.configs.db import db
from shared.models.course_certificate_validity import CourseCertificateValidity
from shared.models.course_class_type import CourseClassType
from shared.models.course_type import CourseType

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

    def create(self, body: dict, actor_id: str) -> dict:
        option_type = body["option_type"]

        if option_type == "type":
            course_type = CourseType(
                sanity_id=body["sanity_id"],
                title=body["title"],
                code=body["code"],
                synced_at=config_module.TIMESTAMP,
                created_at=config_module.TIMESTAMP,
                created_by=actor_id,
            )
            db.save(course_type)

            return {
                "sanity_id": course_type.sanity_id,
                "title": course_type.title,
                "code": course_type.code,
                "synced_at": course_type.synced_at,
            }

        if option_type == "class_type":
            course_class_type = CourseClassType(
                sanity_id=body["sanity_id"],
                title=body["title"],
                synced_at=config_module.TIMESTAMP,
                created_at=config_module.TIMESTAMP,
                created_by=actor_id,
            )
            db.save(course_class_type)
            return {
                "sanity_id": course_class_type.sanity_id,
                "title": course_class_type.title,
                "synced_at": course_class_type.synced_at,
            }

        if option_type == "certificate_validity":
            course_certificate_validity = CourseCertificateValidity(
                sanity_id=body["sanity_id"],
                title=body["title"],
                synced_at=config_module.TIMESTAMP,
                created_at=config_module.TIMESTAMP,
                created_by=actor_id,
            )
            db.save(course_certificate_validity)
            return {
                "sanity_id": course_certificate_validity.sanity_id,
                "title": course_certificate_validity.title,
                "synced_at": course_certificate_validity.synced_at,
            }

        db.commit()

        return {}
