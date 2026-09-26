from typing import TypedDict


class PresignUploadFile(TypedDict):
    filename: str
    content_type: str
    file_size: int
    document_type: str


class DocumentInput(TypedDict):
    document_type: str
    s3_key: str
    original_filename: str
    content_type: str
    file_size: int
    last_modified_at: str


class DocumentRow(TypedDict):
    id: str
    document_type: str
    s3_key: str


class DocumentDeletionRow(TypedDict):
    document_id: str
    s3_key: str


class DocumentMetadataRow(TypedDict):
    id: str
    document_type: str
    original_filename: str
    content_type: str
    file_size: int
    last_modified_at: str
    uploaded_at: str


class PresignUploadResult(TypedDict):
    files: list[dict[str, str]]
    expires_in: int


class SaveDocumentsResult(TypedDict):
    documents: list[DocumentMetadataRow]


class PresignDownloadResult(TypedDict):
    download_url: str
    expires_in: int
