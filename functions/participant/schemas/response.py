from typing import TypedDict

from functions.documents.schemas.document import DocumentMetadataRow
from shared.schemas.response import Metadata

from .participant import DetailParticipantRow


class PaginatedParticipantsResponse(TypedDict):
    participants: list
    metadata: Metadata


class GetDetailParticipantResponse(TypedDict):
    participant: DetailParticipantRow
    documents: list[DocumentMetadataRow]
