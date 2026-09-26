from typing import NotRequired, TypedDict

from functions.documents.schemas.document import DocumentMetadataRow


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
    created_at: NotRequired[str]
    updated_at: NotRequired[str | None]


class GetDetailParticipantResult(TypedDict):
    participant: DetailParticipantRow
    documents: list[DocumentMetadataRow]


class CreateParticipantResult(TypedDict):
    participant: DetailParticipantRow


class ParticipantOwnerRow(TypedDict):
    id: str
