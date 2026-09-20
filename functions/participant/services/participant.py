from ..repositories.participant import ParticipantRepository
from ..schemas.event import GetParticipantsParams
from ..schemas.participant import GetDetailParticipantResult, GetParticipantsResult


class ParticipantService:
    def __init__(self):
        self.repo = ParticipantRepository()

    def get_list(self, params: GetParticipantsParams) -> GetParticipantsResult:
        p = params.get("p") or 1
        rp = params.get("rp") or 25

        participants = self.repo.get_participants(offset=((p - 1) * rp), limit=rp)
        total_data = self.repo.get_total_data_participants()

        return GetParticipantsResult(participants=participants, total_data=total_data)

    def get_detail(self) -> GetDetailParticipantResult:

        participant = self.repo.get_detail_participant()
        if not participant:
            return GetDetailParticipantResult(participant={}, documents=[])

        return GetDetailParticipantResult(participant=participant, documents=[])
