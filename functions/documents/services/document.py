import os
import re
from datetime import datetime
from uuid import UUID, uuid4

from botocore.exceptions import BotoCoreError, ClientError
from sqlalchemy.exc import IntegrityError

from shared import AWSManager
from shared.configs.db import db
from shared.exception import BadRequest, Conflict, NotFound, TooLarge
from shared.util import HttpError

from ..repositories.document import DocumentRepository
from functions.participant.repositories.participant import ParticipantRepository
from ..schemas.document import DocumentInput, PresignDownloadResult, PresignUploadFile, PresignUploadResult, SaveDocumentsResult

MAX_FILE_SIZE = 1024 * 1024
UPLOAD_URL_TTL_SECONDS = 15 * 60
DOWNLOAD_URL_TTL_SECONDS = 60 * 60
DOCUMENT_TYPES = {
    "passport_photo": {"image/jpeg", "image/png"},
    "identity_card": {"image/jpeg", "image/png", "application/pdf"},
    "tax_number": {"image/jpeg", "image/png", "application/pdf"},
    "curiculum_vitae": {"application/pdf"},
    "employment_certificate": {"image/jpeg", "image/png", "application/pdf"},
    "medical_certificate": {"image/jpeg", "image/png", "application/pdf"},
    "integrity_pact": {"image/jpeg", "image/png", "application/pdf"},
    "degree_certificate": {"image/jpeg", "image/png", "application/pdf"},
}


class DocumentService:
    def __init__(self):
        self.repo = DocumentRepository()
        self.participants = ParticipantRepository()
        self.s3_manager = AWSManager.S3Manager(os.environ["S3_BUCKET"])

    def _owner_id(self, value: str) -> UUID:
        try:
            owner_id = UUID(value)
        except (TypeError, ValueError) as exc:
            raise BadRequest("INVALID_OWNER", "owner.id must be a UUID") from exc
        if not self.participants.get_active_owner(owner_id):
            raise NotFound("PARTICIPANT_NOT_FOUND", "Participant not found")
        return owner_id

    @staticmethod
    def _validate_file(document_type: str, content_type: str, file_size: int) -> None:
        if document_type not in DOCUMENT_TYPES or content_type not in DOCUMENT_TYPES[document_type]:
            raise BadRequest("INVALID_DOCUMENT", "Document type or content type is invalid")
        if type(file_size) is not int or file_size <= 0:
            raise BadRequest("INVALID_DOCUMENT", "file_size must be a positive integer")
        if file_size > MAX_FILE_SIZE:
            raise TooLarge("FILE_TOO_LARGE", "Each document must be at most 1 MiB")

    def presign_upload(self, owner_value: str, files: list[PresignUploadFile]) -> PresignUploadResult:
        owner_id = self._owner_id(owner_value)
        if not files or len(files) > len(DOCUMENT_TYPES):
            raise BadRequest("INVALID_FILES", "Provide 1 to 8 files")
        if len({item["document_type"] for item in files}) != len(files):
            raise BadRequest("INVALID_FILES", "Each document type may appear once")

        uploads = []
        for item in files:
            self._validate_file(item["document_type"], item["content_type"], item["file_size"])
            filename = re.sub(r"[^a-zA-Z0-9._-]", "_", item["filename"].strip()).strip("_")[:100] or "file"
            key = f"documents/participant/{owner_id}/{uuid4()}-{filename}"
            try:
                url = self.s3_manager.generate_presigned_url(
                    "put_object",
                    Params={"Key": key, "ContentType": item["content_type"]},
                    ExpiresIn=UPLOAD_URL_TTL_SECONDS,
                )
            except (BotoCoreError, ClientError) as exc:
                raise HttpError(502, "S3_UNAVAILABLE", "Could not sign upload URL") from exc
            uploads.append({"s3_key": key, "upload_url": url})
        return PresignUploadResult(files=uploads, expires_in=UPLOAD_URL_TTL_SECONDS)

    def presign_download(self, document_value: str) -> PresignDownloadResult:
        try:
            document_id = UUID(document_value)
        except (TypeError, ValueError) as exc:
            raise BadRequest("INVALID_DOCUMENT", "document_id must be a UUID") from exc
        document = self.repo.get_active_document(document_id)
        if not document:
            raise NotFound("DOCUMENT_NOT_FOUND", "Document not found")
        try:
            url = self.s3_manager.generate_presigned_url(
                "get_object",
                Params={"Key": document["s3_key"]},
                ExpiresIn=DOWNLOAD_URL_TTL_SECONDS,
            )
        except (BotoCoreError, ClientError) as exc:
            raise HttpError(502, "S3_UNAVAILABLE", "Could not sign download URL") from exc
        return PresignDownloadResult(download_url=url, expires_in=DOWNLOAD_URL_TTL_SECONDS)

    def save_documents(
        self,
        owner_value: str,
        documents: list[DocumentInput],
        remove_values: list[str],
        actor_id: UUID,
    ) -> SaveDocumentsResult:
        owner_id = self._owner_id(owner_value)
        if not documents and not remove_values:
            raise BadRequest("INVALID_DOCUMENTS", "documents or remove_ids is required")
        if len(documents) > len(DOCUMENT_TYPES) or len(remove_values) > len(DOCUMENT_TYPES):
            raise BadRequest("INVALID_DOCUMENTS", "At most 8 documents are allowed")

        try:
            remove_ids = {UUID(value) for value in remove_values}
        except (TypeError, ValueError) as exc:
            raise BadRequest("INVALID_DOCUMENTS", "remove_ids must contain UUIDs") from exc
        if len(remove_ids) != len(remove_values):
            raise BadRequest("INVALID_DOCUMENTS", "remove_ids must be unique")

        existing = self.repo.list_for_owner(owner_id)
        existing_by_id = {item["id"]: item for item in existing}
        pending = self.repo.pending_for_owner(owner_id, remove_ids)
        pending_ids = {item["document_id"] for item in pending}
        if not {str(item) for item in remove_ids} <= existing_by_id.keys() | pending_ids:
            raise NotFound("DOCUMENT_NOT_FOUND", "Document does not belong to participant")
        removed = [item for item in existing if UUID(item["id"]) in remove_ids]
        remaining_types = {
            item["document_type"] for item in existing if UUID(item["id"]) not in remove_ids
        }
        new_types = [item["document_type"] for item in documents]
        if len(set(new_types)) != len(new_types) or set(new_types) & remaining_types:
            raise Conflict("DOCUMENT_ALREADY_EXISTS", "Each document type has one slot")
        if len({item["s3_key"] for item in documents}) != len(documents):
            raise BadRequest("INVALID_DOCUMENTS", "s3_key values must be unique")

        additions = []
        for item in documents:
            self._validate_file(item["document_type"], item["content_type"], item["file_size"])
            key = item["s3_key"]
            prefix = f"documents/participant/{owner_id}/"
            if not key.startswith(prefix) or not key[len(prefix):] or "/" in key[len(prefix):]:
                raise BadRequest("INVALID_DOCUMENT", "s3_key does not belong to participant")
            if not item["original_filename"].strip():
                raise BadRequest("INVALID_DOCUMENT", "original_filename is required")
            try:
                last_modified = datetime.fromisoformat(item["last_modified_at"])
            except (TypeError, ValueError) as exc:
                raise BadRequest("INVALID_DOCUMENT", "last_modified_at must be a timestamp") from exc
            if last_modified.tzinfo is None:
                raise BadRequest("INVALID_DOCUMENT", "last_modified_at must include a timezone")
            try:
                actual = self.s3_manager.head_object(Key=key)
            except ClientError as exc:
                code = exc.response.get("Error", {}).get("Code", "")
                if code in {"404", "NoSuchKey", "NotFound"}:
                    raise BadRequest("UPLOAD_NOT_FOUND", "Uploaded document was not found") from exc
                raise HttpError(502, "S3_UNAVAILABLE", "Could not inspect upload") from exc
            except BotoCoreError as exc:
                raise HttpError(502, "S3_UNAVAILABLE", "Could not inspect upload") from exc
            if actual.get("ContentLength") != item["file_size"] or actual.get("ContentType") != item["content_type"]:
                raise BadRequest("UPLOAD_MISMATCH", "Uploaded document size or type does not match")
            additions.append({
                "document_type": item["document_type"],
                "s3_key": key,
                "original_filename": item["original_filename"].strip(),
                "content_type": item["content_type"],
                "file_size": item["file_size"],
                "last_modified_at": last_modified,
            })

        try:
            metadata = self.repo.save(owner_id, actor_id, additions, removed)
            db.commit()
        except IntegrityError as exc:
            if any(name in str(exc.orig) for name in ("documents_participant_type_key", "documents_s3_key_key")):
                raise Conflict("DOCUMENT_ALREADY_EXISTS", "Document slot or S3 key already exists") from exc
            raise
        for item in self.repo.pending_for_owner(owner_id, remove_ids):
            try:
                self.s3_manager.delete_object(Key=item["s3_key"])
            except (BotoCoreError, ClientError) as exc:
                raise HttpError(502, "S3_CLEANUP_PENDING", "Retry removal with the same remove_ids") from exc
            self.repo.clear_pending(UUID(item["document_id"]))
            db.commit()
        return SaveDocumentsResult(documents=metadata)
