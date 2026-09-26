from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.instructor import Instructor
from shared.models.user import User
from shared.util import serialize

from ..schemas.instructor import DetailInstructorRow, InstructorRow


class InstructorRepository:
    def get_instructors(self, offset: int, limit: int) -> list[InstructorRow]:

        query = (
            select(
                Instructor.id,
                Instructor.name,
                Instructor.phone_number,
                Instructor.email,
                Instructor.course_theme_id,
                Instructor.specialization,
                Instructor.created_at,
                User.name.label("created_by"),
            )
            .select_from(Instructor)
            .join(User, User.id == Instructor.created_by)
            .where(Instructor.is_deleted.is_(False))
            .limit(limit)
            .offset(offset)
        )

        instructors = serialize(db.session.execute(query).all(), InstructorRow)

        return instructors

    def get_total_data_instructors(self) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from(
                    (
                        select(Instructor)
                        .select_from(Instructor)
                        .where(Instructor.is_deleted.is_(False))
                    ).subquery()
                )
            ).first()
            or 0
        )

        return total_data

    def get_detail_instructor(self, instructor_id: str) -> DetailInstructorRow | None:

        instructor = serialize(
            db.session.execute(
                select(Instructor)
                .select_from(Instructor)
                .where(
                    (Instructor.is_deleted.is_(False))
                    & (Instructor.id == func.uuid_to_bin(instructor_id))
                )
            ).first(),
            DetailInstructorRow,
        )

        return instructor
