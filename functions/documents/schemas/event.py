from enum import StrEnum
from typing import NotRequired, TypedDict


class FileOwnerType(StrEnum):
    PARTICIPANT = "participant"
    INSTRUCTOR = "instructor"


class PresignedUploadOwner(TypedDict):
    id: str
    type: FileOwnerType


class PresignedUploadFile(TypedDict):
    filename: str
    document_type: str
    content_type: str


class SaveDocumentFile(TypedDict):
    s3_key: str
    document_type: str


class PresignedUploadEventBody(TypedDict):
    owner: PresignedUploadOwner
    files: list[PresignedUploadFile]


class SaveDocumentEventBody(TypedDict):
    owner: PresignedUploadOwner
    files: list[SaveDocumentFile]
    removed_ids: NotRequired[list[str]]
