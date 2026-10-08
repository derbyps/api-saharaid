from shared import util

from ..schemas.response import GetStatisticResponse
from ..services.statistic import StatisticService


def get_statistic_handler(event: dict) -> dict:
    util.current_user_id(event)

    service = StatisticService()
    result = service.get_statistic()

    response: GetStatisticResponse = {
        "number_stats": {
            "participant": result["number_stats"]["participant"],
            "instructor": result["number_stats"]["instructor"],
            "course": result["number_stats"]["course"],
        },
        "chart_stats": {
            "participant_certificate": [
                {
                    "period": item["period"],
                    "participant": item["participant"],
                    "certificate": item["certificate"],
                }
                for item in result["participant_certificate"]
            ],
        },
    }

    return util.return_response(200, dict(response))
