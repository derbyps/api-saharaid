import os
import re

from botocore.exceptions import BotoCoreError, ClientError

from shared import AWSManager
from shared.configs import config
from shared.configs.db import db
from shared.exception import BadRequest, NotFound, TooLarge
from shared.models.document import Document
from shared.util import HttpError

from ..repositories.document import DocumentRepository
from ..repositories.instructor import InstructorRepository
from ..repositories.participant import ParticipantRepository
from ..schemas.document import PresignUploadResult
from ..schemas.event import (
    FileOwnerType,
    PresignedUploadFile,
    PresignedUploadOwner,
    SaveDocumentFile,
)

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
        self.participant_repo = ParticipantRepository()
        self.instructor_repo = InstructorRepository()
        self.s3_manager = AWSManager.S3Manager(os.environ["S3_BUCKET"])

    @staticmethod
    def _validate_file(
        document_type: str,
        content_type: str,
        file_size: int,
    ) -> None:
        if (
            not re.fullmatch(r"[a-z][a-z0-9_]*", document_type)
            or not content_type.strip()
            or (
                document_type in DOCUMENT_TYPES
                and content_type not in DOCUMENT_TYPES[document_type]
            )
        ):
            raise BadRequest(
                "INVALID_DOCUMENT", "Document type or content type is invalid"
            )

        if type(file_size) is not int or file_size <= 0:
            raise BadRequest("INVALID_DOCUMENT", "file_size must be a positive integer")

        if file_size > MAX_FILE_SIZE:
            raise TooLarge("FILE_TOO_LARGE", "Each document must be at most 1 MiB")

    def presign_upload(
        self, owner: PresignedUploadOwner, files: list[PresignedUploadFile]
    ) -> PresignUploadResult:

        if not files or len(files) > len(DOCUMENT_TYPES):
            raise BadRequest("INVALID_FILES", "Provide 1 to 8 files")

        uploads = []
        for item in files:
            key = f"docs/{owner['type']}/{owner['id']}/{item['document_type']}"

            try:
                url = self.s3_manager.generate_presigned_url(
                    "put_object",
                    Params={"Key": key, "ContentType": item["content_type"]},
                    ExpiresIn=UPLOAD_URL_TTL_SECONDS,
                )

            except (BotoCoreError, ClientError) as exc:
                raise HttpError(
                    502, "S3_UNAVAILABLE", "Could not sign upload URL"
                ) from exc

            uploads.append({"s3_key": key, "upload_url": url})

        return PresignUploadResult(files=uploads, expires_in=UPLOAD_URL_TTL_SECONDS)

    # def presign_download(self, document_value: str) -> PresignDownloadResult:
    #     try:
    #         document_id = UUID(document_value)
    #     except (TypeError, ValueError) as exc:
    #         raise BadRequest("INVALID_DOCUMENT", "document_id must be a UUID") from exc

    #     document = self.repo.get_active_document(document_id)
    #     if not document:
    #         raise NotFound("DOCUMENT_NOT_FOUND", "Document not found")

    #     try:
    #         url = self.s3_manager.generate_presigned_url(
    #             "get_object",
    #             Params={"Key": document["s3_key"]},
    #             ExpiresIn=DOWNLOAD_URL_TTL_SECONDS,
    #         )
    #     except (BotoCoreError, ClientError) as exc:
    #         raise HttpError(
    #             502, "S3_UNAVAILABLE", "Could not sign download URL"
    #         ) from exc

    #     return PresignDownloadResult(
    #         download_url=url, expires_in=DOWNLOAD_URL_TTL_SECONDS
    #     )

    def _is_owner_valid(self, owner: PresignedUploadOwner) -> bool:

        if owner["type"] == FileOwnerType.PARTICIPANT:
            participant = self.participant_repo.find(owner["id"])

            return participant is not None

        if owner["type"] == FileOwnerType.INSTRUCTOR:
            instructor = self.instructor_repo.find(owner["id"])

            return instructor is not None

        return False

    def save_documents(
        self,
        owner: PresignedUploadOwner,
        files: list[SaveDocumentFile],
        removed_ids: list[str],
    ) -> None:

        if not self._is_owner_valid(owner):
            raise NotFound("OWNER_NOT_FOUND", "Owner not found")

        self.repo.remove(removed_ids)

        documents = []
        for item in files:
            documents.append(
                Document(
                    owner_id=owner["id"],
                    owner_type=owner["type"],
                    document_type=item["document_type"],
                    s3_key=item["s3_key"],
                    created_by=config.USER_ID,
                    created_at=config.TIMESTAMP,
                )
            )

        db.session.bulk_save_objects(documents)
        db.session.commit()
