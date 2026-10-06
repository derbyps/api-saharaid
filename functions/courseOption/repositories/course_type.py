from sqlalchemy import select

from shared.configs.db import db
from shared.models.course_type import CourseType


class CourseTypeRepository:
    def get_type(
        self,
    ) -> list[CourseType]:

        course_class_type = (
            list(
                db.session.scalars(
                    select(CourseType)
                    .select_from(CourseType)
                    .where(CourseType.is_deleted == False)
                ).all()
            )
            or []
        )

        return course_class_type
