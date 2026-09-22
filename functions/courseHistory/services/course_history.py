from shared.exception import NotFound

from ..repositories.participant import ParticipantRepository
from ..schemas.participant import GetDetailParticipantResult


class CourseHistoryService:
    def __init__(self):
        self.repo = ParticipantRepository()

    def get_detail(self, participant_id: str) -> GetDetailParticipantResult:

        participant = self.repo.get_detail_participant(participant_id)
        if not participant:
            raise NotFound("COURSE_HISTORY_NOT_FOUND")

        return GetDetailParticipantResult(participant=participant, documents=[])
