from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.DELETE import delete_method_handler
from .handlers.GET import get_schedule_detail_handler, get_schedules_handler
from .handlers.POST import create_schedule_handler
from .handlers.PUT import update_schedule_handler


@handle_errors
def lambda_handler(event, _):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET" and "id" in (event.get("pathParameters") or {}):
        return get_schedule_detail_handler(event)

    if method == "GET":
        return get_schedules_handler(event)

    if method == "POST":
        return create_schedule_handler(event)

    if method == "PUT":
        return update_schedule_handler(event)

    if method == "DELETE":
        return delete_method_handler(event)

    raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")
