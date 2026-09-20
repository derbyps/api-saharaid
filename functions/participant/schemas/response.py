from typing import TypedDict

from shared.schemas.response import Metadata


class PaginatedParticipantsResponse(TypedDict):
    participants: list
    metadata: Metadata
