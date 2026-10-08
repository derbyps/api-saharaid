import json

from shared import util

from ..schemas.schedule import DetailScheduleRow
from ..services.schedule import ScheduleService


def create_schedule_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = [
        "course_id",
        "course_class_type_id",
        "start_date",
        "end_date",
        "location",
        "batch",
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    actor_id = util.current_user_id(event)
    service = ScheduleService()
    result = service.create(body, str(actor_id))
    response: DetailScheduleRow = {
        "id": str(result.id),
        "course_id": str(result.course_id),
        "start_date": result.start_date,
        "end_date": result.end_date,
        "location": result.location,
        "course_class_type_id": result.course_class_type_id,
        "serial_number": result.serial_number,
        "batch": result.batch,
    }

    return util.return_response(201, dict(response))
