from sqlalchemy import select

from shared.configs.db import db
from shared.models.instructor import Instructor


class InstructorRepository:
    def find(self, id: str) -> Instructor | None:
        return db.session.scalars(
            select(Instructor).select_from(Instructor).where(Instructor.id == id)
        ).first()
