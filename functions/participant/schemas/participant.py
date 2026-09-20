from typing import TypedDict


class ParticipantRow(TypedDict):
    id: str
    name: int


class GetParticipantsResult(TypedDict):
    participants: list[ParticipantRow]
    total_data: int
