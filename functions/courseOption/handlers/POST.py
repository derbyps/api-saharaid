import json

from shared import util

from ..services.course_option import CourseOptionService


def create_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = ["option_type"]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    actor_id = util.current_user_id(event)
    service = CourseOptionService()
    result = service.create(body, str(actor_id))

    return util.return_response(201, result)
