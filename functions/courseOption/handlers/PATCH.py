import json

from shared import util

from ..services.course_option import CourseOptionService


def patch_handler(event: dict) -> dict:
    id = (event.get("pathParameters") or {}).get("id")
    if not id:
        return util.return_response(400, {})

    body = json.loads(event.get("body") or "{}")
    req_body = ["option_type"]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    actor_id = util.current_user_id(event)
    service = CourseOptionService()
    response = service.delete(body, id, str(actor_id))

    return util.return_response(201, {"participant": dict(response)})
