from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.course import Course
from shared.models.participant import Participant
from shared.models.schedule import Schedule
from shared.models.schedule_participant import ScheduleParticipant
from shared.util import serialize

from ..schemas.enrollment import EnrollmentRow


class EnrollmentRepository:
    def get_enrollments(self, offset: int, limit: int) -> list[EnrollmentRow]:

        query = (
            select(
                ScheduleParticipant.id,
                Course.id.label("course_id"),
                Schedule.id.label("schedule_id"),
                Participant.name.label("participant_name"),
                Course.name.label("course_name"),
                Schedule.start_date.label("start_date"),
                Schedule.end_date.label("end_date"),
                Schedule.created_at.label("enroll_date"),
                Schedule.serial_number.label("serial_number"),
            )
            .select_from(ScheduleParticipant)
            .join(Schedule, Schedule.id == ScheduleParticipant.schedule_id)
            .join(Course, Course.id == Schedule.course_id)
            .join(Participant, Participant.id == ScheduleParticipant.participant_id)
            .limit(limit)
            .offset(offset)
        )

        enrollments = serialize(db.session.execute(query).all(), EnrollmentRow)

        return enrollments

    def get_total_data_enrollments(self) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from(
                    (
                        select(
                            ScheduleParticipant.id,
                            Course.id.label("course_id"),
                            Schedule.id.label("schedule_id"),
                            Participant.name.label("participant_name"),
                            Course.name.label("course_name"),
                            Schedule.start_date.label("start_date"),
                            Schedule.end_date.label("end_date"),
                            Schedule.created_at.label("enroll_date"),
                            Schedule.serial_number.label("serial_number"),
                        )
                        .select_from(ScheduleParticipant)
                        .join(Schedule, Schedule.id == ScheduleParticipant.schedule_id)
                        .join(Course, Course.id == Schedule.course_id)
                        .join(
                            Participant,
                            Participant.id == ScheduleParticipant.participant_id,
                        )
                    ).subquery()
                )
            ).first()
            or 0
        )

        return total_data
