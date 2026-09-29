from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.POST import login_handler


@handle_errors
def lambda_handler(event, _):
    if event.get("requestContext", {}).get("http", {}).get("method") == "POST":
        return login_handler(event)

    raise util.HttpError(404, "NOT_FOUND", "Route not found")
