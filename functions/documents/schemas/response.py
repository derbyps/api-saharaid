from typing import TypedDict

from .document import DocumentMetadataRow


class PresignUploadResponse(TypedDict):
    files: list[dict[str, str]]
    expires_in: int


class SaveDocumentsResponse(TypedDict):
    documents: list[DocumentMetadataRow]


class PresignDownloadResponse(TypedDict):
    download_url: str
    expires_in: int
