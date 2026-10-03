import json

from shared import util

from ..schemas.event import PresignedUploadEventBody, SaveDocumentEventBody
from ..schemas.response import PresignUploadResponse
from ..services.document import DocumentService


def _owner(body: dict) -> tuple[str, str]:
    owner = body.get("owner")
    if (
        not isinstance(owner, dict)
        or not isinstance(owner.get("type"), str)
        or not isinstance(owner.get("id"), str)
    ):
        raise util.HttpError(400, "INVALID_OWNER", "owner requires type and id")

    return owner["type"], owner["id"]


def presign_upload_handler(event: dict) -> dict:
    body: PresignedUploadEventBody = json.loads(event.get("body") or "{}")

    files = body.get("files")
    owner = body.get("owner")

    document_service = DocumentService()
    result = document_service.presign_upload(owner, files)

    response: PresignUploadResponse = {
        "files": result["files"],
        "expires_in": result["expires_in"],
    }

    return util.return_response(200, dict(response))


def save_documents_handler(event: dict) -> dict:

    body: SaveDocumentEventBody = json.loads(event.get("body") or "{}")

    files = body.get("files")
    owner = body.get("owner")
    removed_ids = body.get("removed_ids") or []

    document_service = DocumentService()
    document_service.save_documents(owner=owner, files=files, removed_ids=removed_ids)

    return util.return_response(201, {})


def presign_download_handler(event: dict) -> dict:

    return util.return_response(
        200, {"download_url": "https://example.com/download", "expires_in": 3600}
    )

    # body = util.parse_body(event)
    # if (
    #     body.keys() != {"owner_type", "document_id"}
    #     or body["owner_type"] != "participant"
    #     or not isinstance(body["document_id"], str)
    # ):
    #     raise util.HttpError(
    #         400, "INVALID_DOCUMENT", "owner_type and document_id are required"
    #     )
    # util.current_user_id(event)
    # result = DocumentService().presign_download(body["document_id"])
    # response: PresignDownloadResponse = {
    #     "download_url": result["download_url"],
    #     "expires_in": result["expires_in"],
    # }
    # return util.return_response(200, dict(response))
