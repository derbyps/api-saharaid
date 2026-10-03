import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import boto3

from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import NotFound
from shared.helpers.utils import get_s3_signed_url
from shared.models.participant import Participant

from ..repositories.document import DocumentRepository
from ..repositories.participant import ParticipantRepository, ParticipantRow
from ..schemas.document import DocumentsRow
from ..schemas.event import GetParticipantsParams
from ..schemas.participant import GetDetailParticipantResult, GetParticipantsResult


class ParticipantService:
    def __init__(self):
        self.participant_repo = ParticipantRepository()
        self.document_repo = DocumentRepository()

    def get_list(self, params: GetParticipantsParams) -> GetParticipantsResult:

        query = self.participant_repo.generate_get_participants(params)
        rows = self.participant_repo.get_participants(query, params)
        total_data = self.participant_repo.get_total_data_participants(query)

        session = boto3.Session(region_name=os.getenv("REGION"))
        s3_client = session.client("s3")

        participants: list[ParticipantRow] = []
        for row in rows:
            passport_photo = None
            if row.get("passport_photo"):
                passport_photo = get_s3_signed_url(
                    s3_client, row.get("passport_photo") or "", timedelta(days=1)
                )

            participants.append(
                ParticipantRow(
                    id=row["id"],
                    name=row["name"],
                    identity_number=row["identity_number"],
                    gender=row["gender"],
                    phone_number=row["phone_number"],
                    email=row["email"],
                    date_of_birth=row["date_of_birth"],
                    religion=row["religion"],
                    address=row["address"],
                    job_position=row["job_position"],
                    job_company=row["job_company"],
                    education=row["education"],
                    cr_number=row["cr_number"],
                    tax_number=row["tax_number"],
                    serial_number=row["serial_number"],
                    created_at=row["created_at"],
                    passport_photo=passport_photo,
                )
            )

        return GetParticipantsResult(participants=participants, total_data=total_data)

    def get_detail(self, participant_id: str) -> GetDetailParticipantResult:

        participant = self.participant_repo.get_detail_participant(participant_id)
        if not participant:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        documents_row = self.document_repo.get_documents(participant_id)

        session = boto3.Session(region_name=os.getenv("REGION"))
        s3_client = session.client("s3")
        documents: list[DocumentsRow] = []
        for row in documents_row:
            url = None
            if row.get("s3_key"):
                url = get_s3_signed_url(
                    s3_client, row.get("s3_key") or "", timedelta(days=1)
                )

            documents.append(
                DocumentsRow(
                    id=row["id"],
                    owner_id=row["owner_id"],
                    owner_type=row["owner_type"],
                    document_type=row["document_type"],
                    s3_key=url,
                    content_type=row["content_type"],
                )
            )

        return GetDetailParticipantResult(participant=participant, documents=documents)

    def create(self, body: dict, actor_id: str) -> Participant:
        print("create 1", body)
        serial_number = self.participant_repo.get_max_serial_number() + 1

        print("create 2", serial_number, config_module.TIMESTAMP)

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
            created_at=config_module.TIMESTAMP,
        )

        print("create 3")

        db.save(participant)
        print("create 4")
        db.commit()
        print("create 5")

        return participant

    def update(self, participant_id: str, body: dict) -> Participant:
        print("haiiiii update")
        participant = Participant.get_detail(participant_id)
        print("participant nicccc", participant)
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
        db.commit()

        return participant
        return participant
        return participant
        return participant
