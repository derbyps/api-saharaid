from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.GET import get_enrollments_handler
from .handlers.POST import create_enrollment_handler


@handle_errors
def lambda_handler(event, _):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        return get_enrollments_handler(event)

    if method == "POST":
        return create_enrollment_handler(event)

    raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")
