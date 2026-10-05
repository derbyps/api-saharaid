from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import Select, func, select

from shared.configs.db import db
from shared.helpers.utils import convert_int
from shared.models.instructor import Instructor
from shared.models.user import User
from shared.util import serialize

from ..helpers.utils import filter_by_created, sorting_by
from ..schemas.event import GetInstructorsParams
from ..schemas.instructor import DetailInstructorRow, InstructorRow


class InstructorRepository:
    def generate_get_instructors(self, params: GetInstructorsParams) -> Select:
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
        )
        search = params.get("search")
        if search:
            query = query.where(Instructor.name.like(f"%{search}%"))

        filter_param = params.get("created")
        if filter_param:
            now = datetime.now(ZoneInfo("Asia/Jakarta"))
            query = filter_by_created(filter_param, now, query)

        return query

    def get_instructors(
        self, params: GetInstructorsParams, query: Select
    ) -> list[InstructorRow]:

        p = convert_int(params.get("p") or 1)
        rp = convert_int(params.get("rp") or 25)
        offset = (p - 1) * rp

        query = sorting_by(params, query)
        query = query.limit(rp).offset(offset)

        instructors = serialize(db.session.execute(query).all(), InstructorRow)

        return instructors

    def get_total_data_instructors(self, query: Select) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from((query).subquery())
            ).first()
            or 0
        )

        return total_data

    def get_detail_instructor(self, instructor_id: str) -> DetailInstructorRow | None:

        instructor = serialize(
            db.session.execute(
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
                .where(
                    (Instructor.is_deleted == False) & (Instructor.id == instructor_id)
                )
            ).first(),
            DetailInstructorRow,
        )

        return instructor
