from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import Select

from shared.models.participant import Participant

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


def sorting_by(sort_param: str, query: Select) -> Select:
    if sort_param == "newest":
        query = query.order_by(Participant.created_at.desc())
    elif sort_param == "oldest":
        query = query.order_by(Participant.created_at.asc())
    elif sort_param == "name_asc":
        query = query.order_by(Participant.name.asc())
    elif sort_param == "name_desc":
        query = query.order_by(Participant.name.desc())

    return query

    return query
