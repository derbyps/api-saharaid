from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.course import Course
from shared.util import serialize

from ..schemas.participant import DetailParticipantRow


class ParticipantRepository:
    def get_course_history(self, participant_id: str) -> DetailParticipantRow | None:

        participant = serialize(
            db.session.execute(
                select(Course)
                .select_from(Course)
                .where(
                    (Course.is_deleted.is_(False))
                    & (Course.id == func.uuid_to_bin(participant_id))
                )
            ).first(),
            DetailParticipantRow,
        )

        return participant
