from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy import func, select

from shared.configs.db import db
from shared.models.participant import Participant
from shared.util import serialize

from ..helpers.utils import filter_by_created, sorting_by
from ..schemas.event import GetParticipantsParams
from ..schemas.participant import DetailParticipantRow, ParticipantRow


class ParticipantRepository:
    def get_max_serial_number(self) -> int:
        return (
            db.session.scalar(
                select(func.max(Participant.serial_number)).select_from(Participant)
            )
            or 0
        )

    def get_participants(
        self,
        params: GetParticipantsParams,
    ) -> list[ParticipantRow]:

        filter_param = params.get("created") or "last_hour"
        sort_param = params.get("sort") or "newest"

        p = params.get("p") or 1
        rp = params.get("rp") or 25

        now = datetime.now(ZoneInfo("Asia/Jakarta"))

        offset = (p - 1) * rp

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
            .where(Participant.is_deleted == False)
        )

        query = filter_by_created(filter_param, now, query)
        query = sorting_by(sort_param, query)
        query = query.limit(rp).offset(offset)

        participants = serialize(
            db.session.execute(query).all(),
            ParticipantRow,
        )

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

        query = (
            select(
                Participant.id,
                Participant.name,
                Participant.identity_number,
                Participant.gender,
                Participant.phone_number,
                Participant.email,
                Participant.date_of_birth,
                Participant.religion,
                Participant.address,
                Participant.job_position,
                Participant.job_company,
                Participant.education,
                Participant.cr_number,
                Participant.tax_number,
                Participant.serial_number,
                Participant.created_at,
                Participant.updated_at,
            )
            .select_from(Participant)
            .where(
                (Participant.is_deleted == False) & (Participant.id == participant_id)
            )
        )

        print("participant_id===", participant_id)
        participant = serialize(
            db.session.execute(query).first(),
            DetailParticipantRow,
        )

        print("participant===", participant)

        return participant
        return participant
        return participant
        return participant
