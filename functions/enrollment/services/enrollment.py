import uuid

from shared.configs.config import config
from shared.configs.db import db
from shared.models.schedule_participant import ScheduleParticipant

from ..repositories.enrollment import EnrollmentRepository
from ..schemas.enrollment import GetEnrollmentsResult
from ..schemas.event import GetEnrollmentsParams


class EnrollmentService:
    def __init__(self):
        self.repo = EnrollmentRepository()

    def get_list(self, params: GetEnrollmentsParams) -> GetEnrollmentsResult:
        p = int(params.get("p") or 1)
        rp = int(params.get("rp") or 25)

        enrollments = self.repo.get_enrollments(offset=((p - 1) * rp), limit=rp)
        total_data = self.repo.get_total_data_enrollments()

        return GetEnrollmentsResult(enrollments=enrollments, total_data=total_data)

    def create(self, body: dict) -> ScheduleParticipant:
        enrollment = ScheduleParticipant(
            id=uuid.uuid4(),
            schedule_id=body["schedule_id"],
            participant_id=body["participant_id"],
            created_at=config.TIMESTAMP,
            created_by=config.USER_ID,
        )

        db.save(enrollment)
        db.commit()

        return enrollment
