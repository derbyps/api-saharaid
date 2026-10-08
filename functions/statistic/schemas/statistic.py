from typing import TypedDict


class MonthlyTotalRow(TypedDict):
    period: str
    total: int


class NumberStatsResult(TypedDict):
    participant: int
    instructor: int
    course: int


class ParticipantCertificateResult(TypedDict):
    period: str
    participant: int
    certificate: int


class GetStatisticResult(TypedDict):
    number_stats: NumberStatsResult
    participant_certificate: list[ParticipantCertificateResult]
