from shared import util

from ..schemas.response import CourseResponse
from ..services.course import CourseService
from .POST import _course_id
from .validate import parse_course_payload


def update_course_handler(event: dict) -> dict:
    course_id = _course_id(event)
    payload = parse_course_payload(event)
    actor_id = util.current_user_id(event)

    result = CourseService().update(course_id, payload, str(actor_id))
    response: CourseResponse = {"course": result}

    return util.return_response(200, dict(response))
