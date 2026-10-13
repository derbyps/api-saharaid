from sqlalchemy import Select, func, select

from shared.configs.db import db
from shared.helpers.utils import convert_int
from shared.models.course import Course
from shared.models.participant import Participant
from shared.models.schedule import Schedule
from shared.models.schedule_participant import ScheduleParticipant
from shared.util import serialize

from ..schemas.enrollment import EnrollmentRow
from ..schemas.event import GetEnrollmentsParams


class EnrollmentRepository:
    def schedule_exists(self, schedule_id: str) -> bool:
        return (
            db.session.scalar(
                select(Schedule.id).where(
                    (Schedule.id == schedule_id) & (Schedule.is_deleted == False)
                )
            )
            is not None
        )

    def get_active_participant_ids(self, participant_ids: list[str]) -> set[str]:
        return set(
            db.session.scalars(
                select(Participant.id).where(
                    Participant.id.in_(participant_ids)
                    & (Participant.is_deleted == False)
                )
            ).all()
        )

    def get_enrolled_participant_ids(
        self, schedule_id: str, participant_ids: list[str]
    ) -> set[str]:
        return set(
            db.session.scalars(
                select(ScheduleParticipant.participant_id).where(
                    (ScheduleParticipant.schedule_id == schedule_id)
                    & ScheduleParticipant.participant_id.in_(participant_ids)
                    & (ScheduleParticipant.is_deleted == False)
                )
            ).all()
        )

    def _filtered_query(self, params: GetEnrollmentsParams) -> Select:
        enroll_date = ScheduleParticipant.created_at

        query = (
            select(
                ScheduleParticipant.id,
                Course.id.label("course_id"),
                Schedule.id.label("schedule_id"),
                Participant.name.label("participant_name"),
                Course.name.label("course_name"),
                Schedule.start_date.label("start_date"),
                Schedule.end_date.label("end_date"),
                enroll_date.label("enroll_date"),
                Schedule.serial_number.label("serial_number"),
            )
            .select_from(ScheduleParticipant)
            .join(Schedule, Schedule.id == ScheduleParticipant.schedule_id)
            .join(Course, Course.id == Schedule.course_id)
            .join(Participant, Participant.id == ScheduleParticipant.participant_id)
            .where(
                (ScheduleParticipant.is_deleted == False)
                & (Schedule.is_deleted == False)
                & (Participant.is_deleted == False)
            )
        )

        search = params.get("search")
        if search:
            query = query.where(
                Participant.name.like(f"%{search}%") | Course.name.like(f"%{search}%")
            )

        for key, part in (("year", func.year), ("month", func.month), ("day", func.day)):
            value = params.get(key)
            if value:
                query = query.where(part(enroll_date) == convert_int(value))

        return query

    def get_enrollments(
        self, params: GetEnrollmentsParams, offset: int, limit: int
    ) -> list[EnrollmentRow]:
        sort_column = {
            "created_at": ScheduleParticipant.created_at,
            "name": Participant.name,
        }.get((params.get("sort_by") or "").lower(), ScheduleParticipant.created_at)
        order = (
            sort_column.asc() if params.get("order_by") == "asc" else sort_column.desc()
        )

        query = (
            self._filtered_query(params)
            .order_by(order, ScheduleParticipant.id)
            .limit(limit)
            .offset(offset)
        )

        return serialize(db.session.execute(query).all(), EnrollmentRow)

    def get_total_data_enrollments(self, params: GetEnrollmentsParams) -> int:
        return (
            db.session.scalars(
                select(func.COUNT()).select_from(self._filtered_query(params).subquery())
            ).first()
            or 0
        )
