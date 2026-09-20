from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.participant import Participant
from shared.util import serialize

from ..schemas.participant import DetailParticipantRow, ParticipantRow

# JAKARTA = ZoneInfo("Asia/Jakarta")
# PROFILE_FIELDS = (
#     "id",
#     "serial_number",
#     "name",
#     "identity_number",
#     "gender",
#     "phone_number",
#     "email",
#     "date_of_birth",
#     "religion",
#     "address",
#     "job_position",
#     "job_company",
#     "education",
#     "cr_number",
#     "tax_number",
#     "created_at",
#     "updated_at",
# )
# LIST_FIELDS = ("id", "serial_number", "name", "phone_number", "email", "created_at")
# DOCUMENT_FIELDS = (
#     "id",
#     "document_type",
#     "original_filename",
#     "content_type",
#     "file_size",
#     "last_modified_at",
#     "uploaded_at",
# )


# def _data(row, names: tuple[str, ...]) -> dict:
#     return {name: getattr(row, name) for name in names}


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

    def get_detail_participant(self) -> DetailParticipantRow | None:

        participant = serialize(
            db.session.execute(
                select(Participant)
                .select_from(Participant)
                .where(Participant.is_deleted.is_(False))
            ).first(),
            DetailParticipantRow,
        )

        return participant

    # def create_participant(self, values: dict, user_id: UUID) -> dict:
    #     participant = Participant(**values, created_by=user_id)
    #     db.session.add(participant)
    #     db.session.flush()
    #     return _data(participant, PROFILE_FIELDS)

    # def get(self, participant_id: UUID) -> Participant:
    #     participant = db.session.scalar(
    #         select(Participant).where(
    #             Participant.id == participant_id, Participant.is_deleted.is_(False)
    #         )
    #     )
    #     if participant is None:
    #         raise HttpError(404, "PARTICIPANT_NOT_FOUND", "Participant not found")
    #     return participant

    # def detail(self, participant_id: UUID) -> dict:
    #     participant = self.get(participant_id)
    #     documents = db.session.scalars(
    #         select(Document)
    #         .where(Document.participant_id == participant_id)
    #         .order_by(Document.uploaded_at, Document.id)
    #     ).all()
    #     return {
    #         "participant": _data(participant, PROFILE_FIELDS),
    #         "documents": [_data(document, DOCUMENT_FIELDS) for document in documents],
    #     }

    # def update(self, participant_id: UUID, values: dict, user_id: UUID) -> dict:
    #     participant = self.get(participant_id)
    #     for name, value in values.items():
    #         setattr(participant, name, value)
    #     participant.updated_by = user_id
    #     participant.updated_at = datetime.now(JAKARTA)
    #     db.session.flush()
    #     return _data(participant, PROFILE_FIELDS)

    # def list(self, page: int, rows: int, created: str | None, sort: str) -> dict:
    #     filters = [Participant.is_deleted.is_(False)]
    #     now = datetime.now(JAKARTA)
    #     today = datetime.combine(now.date(), time.min, JAKARTA)
    #     if created == "today":
    #         filters.append(Participant.created_at >= today)
    #         filters.append(Participant.created_at < today + timedelta(days=1))
    #     elif created == "yesterday":
    #         filters.append(Participant.created_at >= today - timedelta(days=1))
    #         filters.append(Participant.created_at < today)
    #     elif created:
    #         periods = {
    #             "last_hour": timedelta(hours=1),
    #             "last_7_days": timedelta(days=7),
    #             "last_30_days": timedelta(days=30),
    #             "last_90_days": timedelta(days=90),
    #             "last_365_days": timedelta(days=365),
    #         }
    #         filters.append(Participant.created_at >= now - periods[created])

    #     order = {
    #         "oldest": (Participant.created_at.asc(), Participant.id.asc()),
    #         "newest": (Participant.created_at.desc(), Participant.id.desc()),
    #         "name_asc": (func.lower(Participant.name).asc(), Participant.id.asc()),
    #         "name_desc": (func.lower(Participant.name).desc(), Participant.id.desc()),
    #     }[sort]
    #     total = db.session.scalar(
    #         select(func.count()).select_from(Participant).where(*filters)
    #     )
    #     participants = db.session.scalars(
    #         select(Participant)
    #         .where(*filters)
    #         .order_by(*order)
    #         .offset((page - 1) * rows)
    #         .limit(rows)
    #     ).all()
    #     return {
    #         "data": [_data(participant, LIST_FIELDS) for participant in participants],
    #         "pagination": {"p": page, "rp": rows, "total": total},
    #     }
    #     }
    #     }
