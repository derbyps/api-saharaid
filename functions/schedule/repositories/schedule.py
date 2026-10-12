from sqlalchemy import Select, func, select

from shared.configs.db import db
from shared.helpers.utils import convert_int
from shared.models.course import Course
from shared.models.course_class_type import CourseClassType
from shared.models.participant import Participant
from shared.models.schedule import Schedule
from shared.models.schedule_participant import ScheduleParticipant
from shared.util import serialize

from ..schemas.event import GetSchedulesParams
from ..schemas.schedule import DetailScheduleRow, ScheduleRow


class ScheduleRepository:
    def get_max_serial_number(self) -> int:
        return (
            db.session.scalar(
                select(func.max(Schedule.serial_number)).select_from(Schedule)
            )
            or 0
        )

    def generate_get_schedules(self, params: GetSchedulesParams) -> Select:

        participant_count = (
            select(func.count(ScheduleParticipant.id))
            .where(
                (ScheduleParticipant.schedule_id == Schedule.id)
                & (ScheduleParticipant.is_deleted == False)
            )
            .correlate(Schedule)
            .scalar_subquery()
        )

        query = (
            select(
                Schedule.id,
                Schedule.serial_number,
                Course.name.label("course_name"),
                Schedule.batch,
                CourseClassType.title.label("class_type"),
                Schedule.location,
                Schedule.start_date,
                Schedule.end_date,
                participant_count.label("participant_count"),
                Schedule.created_at,
            )
            .select_from(Schedule)
            .join(Course, Course.id == Schedule.course_id)
            .outerjoin(
                CourseClassType, CourseClassType.id == Schedule.course_class_type_id
            )
            .where(Schedule.is_deleted == False)
        )

        search = params.get("search")
        if search:
            query = query.where(Course.name.like(f"%{search}%"))

        return query

    def get_schedules(
        self,
        query: Select,
        params: GetSchedulesParams,
    ) -> list[ScheduleRow]:

        p = convert_int(params.get("p") or 1)
        rp = convert_int(params.get("rp") or 25)
        offset = (p - 1) * rp

        sort_column = {"created_at": Schedule.created_at, "name": Course.name}.get(
            (params.get("sort_by") or "").lower(), Schedule.created_at
        )
        order = (
            sort_column.asc() if params.get("order_by") == "asc" else sort_column.desc()
        )

        query = query.order_by(order, Schedule.serial_number).limit(rp).offset(offset)

        schedules = serialize(db.session.execute(query).all(), ScheduleRow)

        return schedules

    def get_total_data_schedules(self, query: Select) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from((query).subquery())
            ).first()
            or 0
        )

        return total_data

    def get_detail_schedule(self, schedule_id: str) -> DetailScheduleRow | None:

        schedule = serialize(
            db.session.execute(
                select(
                    Schedule.id,
                    Schedule.serial_number,
                    Course.name,
                    Participant.phone_number,
                    Participant.email,
                )
                .select_from(Schedule)
                .join(Course, Course.id == Schedule.course_id)
                .join(
                    ScheduleParticipant, ScheduleParticipant.schedule_id == Schedule.id
                )
                .join(Participant, Participant.id == ScheduleParticipant.participant_id)
                .where((Schedule.is_deleted == False) & (Schedule.id == schedule_id))
            ).first(),
            DetailScheduleRow,
        )

        return schedule
