from sqlalchemy import select

from shared.configs.db import db
from shared.models.course_class_type import CourseClassType


class CourseClassTypeRepository:
    def get_class_type(
        self,
    ) -> list[CourseClassType]:

        course_class_type = (
            list(
                db.session.scalars(
                    select(CourseClassType)
                    .select_from(CourseClassType)
                    .where(CourseClassType.is_deleted == False)
                ).all()
            )
            or []
        )

        return course_class_type
