from typing import TypedDict


class NumberStatsResponse(TypedDict):
    participant: int
    instructor: int
    course: int


class ParticipantCertificateResponse(TypedDict):
    period: str
    participant: int
    certificate: int


class ChartStatsResponse(TypedDict):
    participant_certificate: list[ParticipantCertificateResponse]


class GetStatisticResponse(TypedDict):
    number_stats: NumberStatsResponse
    chart_stats: ChartStatsResponse
