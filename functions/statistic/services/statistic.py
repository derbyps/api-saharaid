from datetime import datetime
from zoneinfo import ZoneInfo

from ..repositories.statistic import StatisticRepository
from ..schemas.statistic import (
    GetStatisticResult,
    MonthlyTotalRow,
    NumberStatsResult,
    ParticipantCertificateResult,
)

WIB = ZoneInfo("Asia/Jakarta")
TOTAL_CHART_MONTHS = 5


class StatisticService:
    def __init__(self):
        self.statistic_repo = StatisticRepository()

    def get_statistic(self) -> GetStatisticResult:

        number_stats = NumberStatsResult(
            participant=self.statistic_repo.get_total_participants(),
            instructor=self.statistic_repo.get_total_instructors(),
            course=self.statistic_repo.get_total_courses(),
        )

        periods = self.get_last_periods(datetime.now(WIB), TOTAL_CHART_MONTHS)
        start_at = f"{periods[0]}-01 00:00:00"

        monthly_participants = self.statistic_repo.get_monthly_participants(start_at)
        monthly_certificates = self.statistic_repo.get_monthly_certificates(start_at)

        participant_by_period = self.map_total_by_period(monthly_participants)
        certificate_by_period = self.map_total_by_period(monthly_certificates)

        participant_certificate: list[ParticipantCertificateResult] = []
        for period in periods:
            participant_certificate.append(
                ParticipantCertificateResult(
                    period=period,
                    participant=participant_by_period.get(period, 0),
                    certificate=certificate_by_period.get(period, 0),
                )
            )

        return GetStatisticResult(
            number_stats=number_stats,
            participant_certificate=participant_certificate,
        )

    def get_last_periods(self, now: datetime, total_months: int) -> list[str]:
        """Return `YYYY-MM` periods for the last months, oldest first, ending with now."""

        periods: list[str] = []
        for months_ago in range(total_months - 1, -1, -1):
            month_index = now.year * 12 + (now.month - 1) - months_ago
            year, month = divmod(month_index, 12)
            periods.append(f"{year:04d}-{month + 1:02d}")

        return periods

    def map_total_by_period(self, rows: list[MonthlyTotalRow]) -> dict[str, int]:

        return {row["period"]: row["total"] for row in rows}
