import json
import unittest
from datetime import datetime
from unittest.mock import Mock, patch
from uuid import uuid4

from functions.statistic.lambda_function import lambda_handler
from functions.statistic.services.statistic import WIB, StatisticService

REPOSITORY = "functions.statistic.services.statistic.StatisticRepository"


def statistic_event(method: str = "GET") -> dict:
    return {"requestContext": {"http": {"method": method}}}


class StatisticTest(unittest.TestCase):
    def test_last_periods_are_ascending_and_cross_year(self):
        service = StatisticService.__new__(StatisticService)

        periods = service.get_last_periods(datetime(2026, 2, 15, tzinfo=WIB), 5)

        self.assertEqual(
            periods, ["2025-10", "2025-11", "2025-12", "2026-01", "2026-02"]
        )

    def test_get_statistic_returns_numbers_and_zero_filled_chart(self):
        statistic_repo = Mock()
        statistic_repo.get_total_participants.return_value = 100
        statistic_repo.get_total_instructors.return_value = 200
        statistic_repo.get_total_courses.return_value = 300
        statistic_repo.get_monthly_participants.return_value = [
            {"period": "2026-08", "total": 7}
        ]
        statistic_repo.get_monthly_certificates.return_value = [
            {"period": "2026-10", "total": 3}
        ]

        with (
            patch("shared.decorators.error_handling.db"),
            patch("shared.util.current_user_id", return_value=uuid4()),
            patch(REPOSITORY, return_value=statistic_repo),
            patch(
                "functions.statistic.services.statistic.datetime",
                Mock(now=Mock(return_value=datetime(2026, 10, 8, tzinfo=WIB))),
            ),
        ):
            response = lambda_handler(statistic_event(), None)

        self.assertEqual(response["statusCode"], 200)
        body = json.loads(response["body"])

        self.assertEqual(
            body["number_stats"],
            {"participant": 100, "instructor": 200, "course": 300},
        )
        self.assertEqual(
            body["chart_stats"]["participant_certificate"],
            [
                {"period": "2026-06", "participant": 0, "certificate": 0},
                {"period": "2026-07", "participant": 0, "certificate": 0},
                {"period": "2026-08", "participant": 7, "certificate": 0},
                {"period": "2026-09", "participant": 0, "certificate": 0},
                {"period": "2026-10", "participant": 0, "certificate": 3},
            ],
        )
        statistic_repo.get_monthly_participants.assert_called_once_with(
            "2026-06-01 00:00:00"
        )

    def test_other_methods_are_rejected(self):
        with patch("shared.decorators.error_handling.db"):
            response = lambda_handler(statistic_event("POST"), None)

        self.assertEqual(response["statusCode"], 405)


if __name__ == "__main__":
    unittest.main()
