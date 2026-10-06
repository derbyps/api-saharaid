from sqlalchemy import select

from shared.configs.db import db
from shared.models.course_certificate_validity import CourseCertificateValidity


class CourseCertificateValidityRepository:
    def get_certificate_validity(
        self,
    ) -> list[CourseCertificateValidity]:

        course_certificate_velidity = (
            list(
                db.session.scalars(
                    select(CourseCertificateValidity)
                    .select_from(CourseCertificateValidity)
                    .where(CourseCertificateValidity.is_deleted == False)
                ).all()
            )
            or []
        )

        return course_certificate_velidity
