from sqlalchemy import func, select, update

from shared.configs.db import db
from shared.models.course import Course
from shared.models.participant import Participant
from shared.models.schedule import Schedule
from shared.models.schedule_participant import ScheduleParticipant
from shared.util import serialize

from ..schemas.schedule import DetailScheduleRow, ScheduleRow


class ScheduleRepository:
    def get_schedules(self, offset: int, limit: int) -> list[ScheduleRow]:

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
            .limit(limit)
            .offset(offset)
        )

        schedules = serialize(db.session.execute(query).all(), ScheduleRow)

        return schedules

    def get_total_data_schedules(self) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from(
                    (
                        select(Schedule)
                        .select_from(Schedule)
                        .where(Schedule.is_deleted == False)
                    ).subquery()
                )
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
