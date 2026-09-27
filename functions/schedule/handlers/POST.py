import json

from shared import util

from ..schemas.schedule import DetailScheduleRow
from ..services.schedule import ScheduleService


def create_schedule_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = [
        "course_id",
        "class",
        "course_mode",
        "start_date",
        "end_date",
        "location",
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    service = ScheduleService()
    result = service.create(body)
    response: DetailScheduleRow = {
        "id": str(result.id),
        "course_id": str(result.course_id),
        "start_date": result.start_date,
        "end_date": result.end_date,
        "location": result.location,
        "course_mode_id": str(result.course_mode_id),
        "serial_number": result.serial_number,
    }

    return util.return_response(201, dict(response))
