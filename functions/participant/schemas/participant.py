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
