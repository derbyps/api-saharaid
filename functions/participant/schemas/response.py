from typing import TypedDict

from shared.schemas.response import Metadata

from functions.documents.schemas.document import DocumentMetadataRow
from .participant import DetailParticipantRow


class PaginatedParticipantsResponse(TypedDict):
    participants: list
    metadata: Metadata


class CreateParticipantResponse(TypedDict):
    participant: DetailParticipantRow


class GetDetailParticipantResponse(TypedDict):
    participant: DetailParticipantRow
    documents: list[DocumentMetadataRow]
