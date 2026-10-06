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
            types = self.type_repo.get_type()
            res = []
            for type in types:
                res.append(
                    {
                        "id": type.id,
                        "sanity_id": type.sanity_id,
                        "title": type.title,
                        "code": type.code,
                        "synced_at": type.synced_at,
                    }
                )
            response["type"] = res

        if include and "class_type" in include:
            class_types = self.class_type_repo.get_class_type()
            res = []
            for class_type in class_types:
                res.append(
                    {
                        "id": class_type.id,
                        "sanity_id": class_type.sanity_id,
                        "title": class_type.title,
                        "synced_at": class_type.synced_at,
                    }
                )

            response["class_type"] = res

        if include and "certificate_validity" in include:
            certificate_validities = (
                self.certificate_validity.get_certificate_validity()
            )
            res = []
            for certificate_validity in certificate_validities:
                res.append(
                    {
                        "id": certificate_validity.id,
                        "sanity_id": certificate_validity.sanity_id,
                        "title": certificate_validity.title,
                        "synced_at": certificate_validity.synced_at,
                    }
                )
            response["certificate_validity"] = res

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
