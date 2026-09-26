from uuid import UUID

from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.participant import Participant
from shared.util import serialize

from ..schemas.event import CreateParticipantBody
from ..schemas.participant import (
    DetailParticipantRow,
    ParticipantOwnerRow,
    ParticipantRow,
)


def _detail_row(participant: Participant) -> DetailParticipantRow:
    return DetailParticipantRow(
        id=str(participant.id),
        serial_number=participant.serial_number,
        name=participant.name,
        identity_number=participant.identity_number,
        gender=participant.gender,
        phone_number=participant.phone_number,
        email=participant.email,
        date_of_birth=participant.date_of_birth.isoformat(),
        religion=participant.religion,
        address=participant.address,
        job_position=participant.job_position,
        job_company=participant.job_company,
        education=participant.education,
        cr_number=participant.cr_number,
        tax_number=participant.tax_number,
        created_at=participant.created_at.isoformat(),
        updated_at=participant.updated_at.isoformat()
        if participant.updated_at
        else None,
    )


class ParticipantRepository:
    def get_active_owner(self, participant_id: UUID) -> ParticipantOwnerRow | None:
        owner_id = db.session.scalar(
            select(Participant.id).where(
                Participant.id == participant_id, Participant.is_deleted.is_(False)
            )
        )
        return ParticipantOwnerRow(id=str(owner_id)) if owner_id else None

    def create(
        self, body: CreateParticipantBody, actor_id: UUID
    ) -> DetailParticipantRow:
        participant = Participant(**body, created_by=actor_id)
        db.session.add(participant)
        db.session.flush()
        db.session.refresh(participant)
        return _detail_row(participant)

    def get_participants(self, offset: int, limit: int) -> list[ParticipantRow]:

        query = (
            select(
                Participant.id,
                Participant.serial_number,
                Participant.name,
                Participant.phone_number,
                Participant.email,
                Participant.created_at,
            )
            .select_from(Participant)
            .where(Participant.is_deleted.is_(False))
            .limit(limit)
            .offset(offset)
        )

        participants = serialize(db.session.execute(query).all(), ParticipantRow)

        return participants

    def get_total_data_participants(self) -> int:

        total_data = (
            db.session.scalars(
                select(func.COUNT()).select_from(
                    (
                        select(Participant)
                        .select_from(Participant)
                        .where(Participant.is_deleted.is_(False))
                    ).subquery()
                )
            ).first()
            or 0
        )

        return total_data

    def get_detail_participant(
        self, participant_id: UUID
    ) -> DetailParticipantRow | None:
        participant = db.session.scalar(
            select(Participant).where(
                Participant.id == participant_id, Participant.is_deleted.is_(False)
            )
        )
        return _detail_row(participant) if participant else None
