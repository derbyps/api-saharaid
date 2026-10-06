from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.GET import get_course_option_handler
from .handlers.POST import create_handler
from .handlers.PUT import update_instructor_handler


@handle_errors
def lambda_handler(event, _):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        return get_course_option_handler(event)

    if method == "POST":
        return create_handler(event)

    if method == "PUT":
        return update_instructor_handler(event)

    raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")
