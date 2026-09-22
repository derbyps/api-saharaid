from typing import TypedDict


class ParticipantRow(TypedDict):
    id: str
    serial_number: int
    name: int
    phone_number: str
    email: str
    created_at: str


class GetParticipantsResult(TypedDict):
    participants: list[ParticipantRow]
    total_data: int


class DocumentsRow(TypedDict):
    id: str
    document_type: str
    original_filename: str
    content_type: str
    file_size: int
    last_modified_at: str
    uploaded_at: str


class DetailParticipantRow(TypedDict):
    id: str
    name: str
    identity_number: str
    gender: str
    phone_number: str
    email: str
    date_of_birth: str
    religion: str
    address: str
    job_position: str
    job_company: str
    education: str
    cr_number: str
    tax_number: str
    serial_number: int


class GetDetailParticipantResult(TypedDict):
    participant: DetailParticipantRow
    documents: list[DocumentsRow]
