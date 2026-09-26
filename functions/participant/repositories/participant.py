from sqlalchemy import func, select, update

from shared.configs.db import db
from shared.models.participant import Participant
from shared.util import serialize

from ..schemas.participant import DetailParticipantRow, ParticipantRow


class ParticipantRepository:
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
        self, participant_id: str
    ) -> DetailParticipantRow | None:

        participant = serialize(
            db.session.execute(
                select(Participant)
                .select_from(Participant)
                .where(
                    (Participant.is_deleted.is_(False))
                    & (Participant.id == func.uuid_to_bin(participant_id))
                )
            ).first(),
            DetailParticipantRow,
        )

        return participant
