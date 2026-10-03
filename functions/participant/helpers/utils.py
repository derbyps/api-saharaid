from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import Select, text

from shared.models.participant import Participant

from ..schemas.event import GetParticipantsParams

WIB = ZoneInfo("Asia/Jakarta")


def filter_by_created(
    created: str,
    now: datetime,
    query: Select,
):
    start_of_today = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )

    if created == "last_hour":
        return query.where(Participant.created_at >= now - timedelta(hours=1))

    if created == "today":
        return query.where(Participant.created_at >= start_of_today)

    if created == "yesterday":
        start_of_yesterday = start_of_today - timedelta(days=1)

        return query.where(
            (Participant.created_at >= start_of_yesterday)
            & (Participant.created_at < start_of_today)
        )

    duration = {
        "last_7_days": timedelta(days=7),
        "last_30_days": timedelta(days=30),
        "last_90_days": timedelta(days=90),
        "last_365_days": timedelta(days=365),
    }

    if created in duration:
        return query.where(Participant.created_at >= now - duration[created])

    return query


def sorting_by(params: GetParticipantsParams, query: Select) -> Select:
    order_by = params.get("order_by") or "asc"
    sorted_by = params.get("sort_by") or "created_at"

    sort_option = {
        "created_at": "created_at",
        "name": "name",
    }

    sort_by = sort_option.get(sorted_by.lower()) or "created_at"

    if order_by == "asc":
        return query.order_by(text(f"{sort_by} ASC"))

    return query.order_by(text(f"{sort_by} DESC"))
