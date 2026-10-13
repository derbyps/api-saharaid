from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import Conflict, NotFound
from shared.models.schedule_participant import ScheduleParticipant

from ..repositories.enrollment import EnrollmentRepository
from ..schemas.enrollment import CreateEnrollmentResult, GetEnrollmentsResult
from ..schemas.event import CreateEnrollmentBody, GetEnrollmentsParams


class EnrollmentService:
    def __init__(self):
        self.repo = EnrollmentRepository()

    def get_list(self, params: GetEnrollmentsParams) -> GetEnrollmentsResult:
        p = int(params.get("p") or 1)
        rp = int(params.get("rp") or 25)

        enrollments = self.repo.get_enrollments(
            params, offset=((p - 1) * rp), limit=rp
        )
        total_data = self.repo.get_total_data_enrollments(params)

        return GetEnrollmentsResult(enrollments=enrollments, total_data=total_data)

    def create(
        self, body: CreateEnrollmentBody, actor_id: str
    ) -> CreateEnrollmentResult:
        schedule_id = body["schedule_id"]
        participant_ids = body["participant_ids"]

        if not self.repo.schedule_exists(schedule_id):
            raise NotFound("SCHEDULE_NOT_FOUND", "Schedule not found")

        active_ids = self.repo.get_active_participant_ids(participant_ids)
        if active_ids != set(participant_ids):
            raise NotFound("PARTICIPANT_NOT_FOUND", "Participant not found")

        if self.repo.get_enrolled_participant_ids(schedule_id, participant_ids):
            raise Conflict(
                "DUPLICATE_ENROLLMENT",
                "Participant is already enrolled in this schedule",
            )

        created_at = config_module.TIMESTAMP
        for participant_id in participant_ids:
            db.save(
                ScheduleParticipant(
                    schedule_id=schedule_id,
                    participant_id=participant_id,
                    created_at=created_at,
                    created_by=actor_id,
                )
            )
        db.commit()

        return CreateEnrollmentResult(inserted=len(participant_ids))
