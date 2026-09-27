from shared import util

from ..schemas.event import GetSchedulesParams
from ..schemas.response import GetDetailScheduleResponse, PaginatedSchedulesResponse
from ..services.schedule import ScheduleService


def get_schedules_handler(event: dict) -> dict:

    params: GetSchedulesParams = event.get("queryStringParameters") or {}

    service = ScheduleService()
    result = service.get_list(params)

    response: PaginatedSchedulesResponse = {
        "schedules": result["schedules"],
        "metadata": {
            "p": params.get("p") or 1,
            "rp": params.get("rp") or 25,
            "total_data": result["total_data"],
        },
    }

    return util.return_response(200, dict(response))


def get_schedule_detail_handler(event: dict) -> dict:
    schedule_id = (event.get("pathParameters") or {}).get("id")
    if not schedule_id:
        raise util.HttpError(400, "INVALID_ID", "id is required")
    util.current_user_id(event)

    service = ScheduleService()
    result = service.get_detail(schedule_id)

    response: GetDetailScheduleResponse = {
        "schedule": result["schedule"],
    }

    return util.return_response(200, dict(response))
