from shared import util

from ..schemas.response import CourseResponse
from ..services.course import CourseService
from .validate import parse_course_payload, parse_finalize_body, parse_presign_body


def _course_id(event: dict) -> str:
    course_id = (event.get("pathParameters") or {}).get("id")
    if not course_id:
        raise util.HttpError(400, "INVALID_ID", "id is required")

    return course_id


def create_course_handler(event: dict) -> dict:
    payload = parse_course_payload(event)
    actor_id = util.current_user_id(event)

    result = CourseService().create(payload, str(actor_id))
    response: CourseResponse = {"course": result}

    return util.return_response(201, dict(response))


def presign_course_upload_handler(event: dict) -> dict:
    course_id = _course_id(event)
    body = parse_presign_body(event)
    util.current_user_id(event)

    result = CourseService().presign(course_id, body)

    return util.return_response(200, dict(result))


def finalize_course_handler(event: dict) -> dict:
    course_id = _course_id(event)
    body = parse_finalize_body(event)
    actor_id = util.current_user_id(event)

    result = CourseService().finalize(course_id, body, str(actor_id))
    response: CourseResponse = {"course": result}

    return util.return_response(200, dict(response))
