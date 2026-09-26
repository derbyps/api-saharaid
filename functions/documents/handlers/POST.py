from shared import util

from ..schemas.document import DocumentInput, PresignUploadFile
from ..schemas.response import PresignDownloadResponse, PresignUploadResponse, SaveDocumentsResponse
from ..services.document import DocumentService


def _owner(body: dict) -> str:
    owner = body.get("owner")
    if not isinstance(owner, dict) or owner.get("type") != "participant" or not isinstance(owner.get("id"), str):
        raise util.HttpError(400, "INVALID_OWNER", "owner must identify a participant")
    return owner["id"]


def presign_upload_handler(event: dict) -> dict:
    body = util.parse_body(event)
    util.current_user_id(event)
    owner_id = _owner(body)
    files = body.get("files")
    fields = PresignUploadFile.__annotations__.keys()
    if not isinstance(files, list) or any(
        not isinstance(item, dict)
        or item.keys() != fields
        or any(not isinstance(item[key], str) for key in ("filename", "content_type", "document_type"))
        or not item["filename"].strip()
        for item in files
    ):
        raise util.HttpError(400, "INVALID_FILES", "files contains invalid entries")
    result = DocumentService().presign_upload(owner_id, files)
    response: PresignUploadResponse = {"files": result["files"], "expires_in": result["expires_in"]}
    return util.return_response(200, response)


def save_documents_handler(event: dict) -> dict:
    body = util.parse_body(event)
    owner_id = _owner(body)
    documents = body.get("documents")
    remove_ids = body.get("remove_ids", [])
    fields = DocumentInput.__annotations__.keys()
    if not isinstance(documents, list) or not isinstance(remove_ids, list) or any(
        not isinstance(item, dict)
        or item.keys() != fields
        or any(not isinstance(item[key], str) for key in fields if key != "file_size")
        for item in documents
    ) or any(not isinstance(item, str) for item in remove_ids):
        raise util.HttpError(400, "INVALID_DOCUMENTS", "documents or remove_ids is invalid")
    result = DocumentService().save_documents(
        owner_id, documents, remove_ids, util.current_user_id(event)
    )
    response: SaveDocumentsResponse = {"documents": result["documents"]}
    return util.return_response(200, response)


def presign_download_handler(event: dict) -> dict:
    body = util.parse_body(event)
    if body.keys() != {"owner_type", "document_id"} or body["owner_type"] != "participant" or not isinstance(body["document_id"], str):
        raise util.HttpError(400, "INVALID_DOCUMENT", "owner_type and document_id are required")
    util.current_user_id(event)
    result = DocumentService().presign_download(body["document_id"])
    response: PresignDownloadResponse = {
        "download_url": result["download_url"], "expires_in": result["expires_in"]
    }
    return util.return_response(200, response)
