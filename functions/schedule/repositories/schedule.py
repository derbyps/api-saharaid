from sqlalchemy import Select, func, select

from shared.configs.db import db
from shared.helpers.utils import convert_int
from shared.models.course import Course
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

        query = (
            select(
                Schedule.id,
                Schedule.serial_number,
                Course.name,
                Participant.phone_number,
                Participant.email,
            )
            .select_from(Schedule)
            .join(Course, Course.id == Schedule.course_id)
            .join(ScheduleParticipant, ScheduleParticipant.schedule_id == Schedule.id)
            .join(Participant, Participant.id == ScheduleParticipant.participant_id)
            .where(Schedule.is_deleted == False)
        )

        return query

    def get_schedules(
        self,
        query: Select,
        params: GetSchedulesParams,
    ) -> list[ScheduleRow]:

        p = convert_int(params.get("p") or 1)
        rp = convert_int(params.get("rp") or 25)
        offset = (p - 1) * rp

        query = query.limit(rp).offset(offset)

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
