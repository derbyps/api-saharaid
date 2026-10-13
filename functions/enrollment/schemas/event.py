from typing import NotRequired, TypedDict


class GetEnrollmentsParams(TypedDict):
    p: NotRequired[int]
    rp: NotRequired[int]
    search: NotRequired[str]
    sort_by: NotRequired[str]
    order_by: NotRequired[str]
    day: NotRequired[int]
    month: NotRequired[int]
    year: NotRequired[int]


class CreateEnrollmentBody(TypedDict):
    schedule_id: str
    participant_ids: list[str]
