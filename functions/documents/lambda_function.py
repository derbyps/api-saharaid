from shared import util
from shared.decorators.error_handling import handle_errors

from .handlers.POST import presign_download_handler, presign_upload_handler, save_documents_handler


@handle_errors
def lambda_handler(event, _):
    if event.get("requestContext", {}).get("http", {}).get("method") != "POST":
        raise util.HttpError(405, "METHOD_NOT_ALLOWED", "Method not allowed")

    path = event.get("rawPath")
    if path == "/files/presign-upload":
        return presign_upload_handler(event)
    if path == "/files/presign-download":
        return presign_download_handler(event)
    if path == "/documents":
        return save_documents_handler(event)
    raise util.HttpError(404, "NOT_FOUND", "Route not found")
