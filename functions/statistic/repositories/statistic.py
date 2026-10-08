from sqlalchemy import func, select, text

from shared.configs.db import db
from shared.models.course import Course
from shared.models.course_certificate_validity import CourseCertificateValidity
from shared.models.instructor import Instructor
from shared.models.participant import Participant
from shared.util import serialize

from ..schemas.statistic import MonthlyTotalRow

PERIOD_FORMAT = "%Y-%m"


class StatisticRepository:
    def get_total_participants(self) -> int:

        total_participants = (
            db.session.scalar(
                select(func.COUNT(Participant.id))
                .select_from(Participant)
                .where(Participant.is_deleted == False)
            )
            or 0
        )

        return total_participants

    def get_total_instructors(self) -> int:

        total_instructors = (
            db.session.scalar(
                select(func.COUNT(Instructor.id))
                .select_from(Instructor)
                .where(Instructor.is_deleted == False)
            )
            or 0
        )

        return total_instructors

    def get_total_courses(self) -> int:

        total_courses = (
            db.session.scalar(
                select(func.COUNT(Course.id))
                .select_from(Course)
                .where(Course.is_deleted == False)
            )
            or 0
        )

        return total_courses

    def get_monthly_participants(self, start_at: str) -> list[MonthlyTotalRow]:

        period = func.date_format(Participant.created_at, PERIOD_FORMAT).label("period")

        query = (
            select(
                period,
                func.COUNT(Participant.id).label("total"),
            )
            .select_from(Participant)
            .where(
                (Participant.is_deleted == False) & (Participant.created_at >= start_at)
            )
            .group_by(text("period"))
        )

        monthly_participants = serialize(
            db.session.execute(query).all(),
            MonthlyTotalRow,
        )

        return monthly_participants

    def get_monthly_certificates(self, start_at: str) -> list[MonthlyTotalRow]:

        period = func.date_format(
            CourseCertificateValidity.created_at, PERIOD_FORMAT
        ).label("period")

        query = (
            select(
                period,
                func.COUNT(CourseCertificateValidity.id).label("total"),
            )
            .select_from(CourseCertificateValidity)
            .where(
                (CourseCertificateValidity.is_deleted == False)
                & (CourseCertificateValidity.created_at >= start_at)
            )
            .group_by(text("period"))
        )

        monthly_certificates = serialize(
            db.session.execute(query).all(),
            MonthlyTotalRow,
        )

        return monthly_certificates
