from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.POST import (
    create_course_handler,
    finalize_course_handler,
    presign_course_upload_handler,
)
from .handlers.PUT import update_course_handler


@handle_errors
def lambda_handler(event, _):
    method = event.get("requestContext", {}).get("http", {}).get("method")
    path = event.get("rawPath", "")

    if method == "POST" and path.endswith("/presign"):
        return presign_course_upload_handler(event)

    if method == "POST" and path.endswith("/finalize"):
        return finalize_course_handler(event)

    if method == "POST":
        return create_course_handler(event)

    if method == "PUT":
        return update_course_handler(event)

    raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")
