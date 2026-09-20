from ..repositories.participant import ParticipantRepository
from ..schemas.event import GetParticipantsParams
from ..schemas.participant import GetParticipantsResult


class ParticipantService:
    def __init__(self):
        self.repo = ParticipantRepository()

    def get_list(self, params: GetParticipantsParams) -> GetParticipantsResult:

        participants = self.repo.get_participants()
        total_data = 0

        return GetParticipantsResult(participants=participants, total_data=total_data)
