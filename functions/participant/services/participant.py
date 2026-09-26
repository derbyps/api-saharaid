from uuid import UUID

from sqlalchemy.exc import IntegrityError

from shared.configs.config import config
from shared.configs.db import db
from shared.exception import BadRequest, Conflict, NotFound
from shared.models.participant import Participant

from functions.documents.repositories.document import DocumentRepository
from ..repositories.participant import ParticipantRepository
from ..schemas.event import CreateParticipantBody, GetParticipantsParams
from ..schemas.participant import CreateParticipantResult, GetDetailParticipantResult, GetParticipantsResult


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
        try:
            owner_id = UUID(participant_id)
        except (TypeError, ValueError) as exc:
            raise BadRequest("INVALID_ID", "id must be a UUID") from exc
        participant = self.repo.get_detail_participant(owner_id)
        if not participant:
            raise NotFound("PARTICIPANT_NOT_FOUND", "Participant not found")

        documents = DocumentRepository().list_metadata_for_owner(owner_id)
        return GetDetailParticipantResult(participant=participant, documents=documents)

    def create(self, body: CreateParticipantBody, actor_id: UUID) -> CreateParticipantResult:
        try:
            participant = self.repo.create(body, actor_id)
            db.commit()
        except IntegrityError as exc:
            if "participants_active_" in str(exc.orig):
                raise Conflict("PARTICIPANT_ALREADY_EXISTS", "Name or phone number already exists") from exc
            raise
        return CreateParticipantResult(participant=participant)

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
        participant.updated_at = config.TIMESTAMP
        participant.updated_by = config.USER_ID

        db.commit()

        return participant
