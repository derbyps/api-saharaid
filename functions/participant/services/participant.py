from datetime import datetime
from zoneinfo import ZoneInfo

from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import NotFound
from shared.models.participant import Participant

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

    def get_detail(self, participant_id: str) -> GetDetailParticipantResult:

        participant = self.repo.get_detail_participant(participant_id)
        if not participant:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        return GetDetailParticipantResult(participant=participant, documents=[])

    def create(self, body: dict, actor_id: str) -> Participant:
        # ponytail: concurrent creates can race; use a locked counter if throughput requires it.
        serial_number = self.repo.get_max_serial_number() + 1

        participant = Participant(
            name=body["name"],
            identity_number=body["identity_number"],
            gender=body["gender"],
            phone_number=body["phone_number"],
            email=body["email"],
            date_of_birth=body["date_of_birth"],
            religion=body["religion"],
            address=body["address"],
            job_position=body["job_position"],
            job_company=body["job_company"],
            education=body["education"],
            cr_number=body["cr_number"],
            tax_number=body["tax_number"],
            serial_number=serial_number,
            created_by=actor_id,
        )

        db.save(participant)
        db.commit()

        return participant

    def update(self, participant_id: str, body: dict) -> Participant:
        participant = Participant.get_detail(participant_id)
        if not participant:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        participant.name = body["name"]
        participant.identity_number = body["identity_number"]
        participant.gender = body["gender"]
        participant.phone_number = body["phone_number"]
        participant.email = body["email"]
        participant.date_of_birth = body["date_of_birth"]
        participant.religion = body["religion"]
        participant.address = body["address"]
        participant.job_position = body["job_position"]
        participant.job_company = body["job_company"]
        participant.education = body["education"]
        participant.cr_number = body["cr_number"]
        participant.tax_number = body["tax_number"]
        participant.updated_at = datetime.now(ZoneInfo("Asia/Jakarta")).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        participant.updated_by = config_module.USER_ID

        db.commit()

        return participant
