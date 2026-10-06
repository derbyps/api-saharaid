from shared import util

from ..schemas.event import GetParams
from ..services.course_option import CourseOptionService


def get_course_option_handler(event: dict) -> dict:
    params: GetParams = event.get("queryStringParameters") or {}

    service = CourseOptionService()
    result = service.get(params)

    return util.return_response(200, dict(result))
