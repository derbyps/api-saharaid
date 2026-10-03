from sqlalchemy import select

from shared.configs.db import db
from shared.models.participant import Participant


class ParticipantRepository:
    def find(self, id: str) -> Participant | None:
        return db.session.scalars(
            select(Participant).select_from(Participant).where(Participant.id == id)
        ).first()
