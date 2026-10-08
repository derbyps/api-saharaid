from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.GET import get_statistic_handler


@handle_errors
def lambda_handler(event, _):
    method = event.get("requestContext", {}).get("http", {}).get("method")

    if method == "GET":
        return get_statistic_handler(event)

    raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")
