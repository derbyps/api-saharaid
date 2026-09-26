import re
from datetime import date

from shared import util

from ..schemas.event import CreateParticipantBody
from ..schemas.response import CreateParticipantResponse
from ..services.participant import ParticipantService


def create_participant_handler(event: dict) -> dict:
    body = util.parse_body(event)
    fields = CreateParticipantBody.__annotations__.keys()
    if body.keys() != fields or any(not isinstance(body[field], str) for field in fields):
        raise util.HttpError(400, "INVALID_BODY", "Participant fields are missing or invalid")

    body = {field: value.strip() for field, value in body.items()}
    if not all(body[field] for field in ("name", "phone_number", "email")):
        raise util.HttpError(400, "INVALID_BODY", "Name, phone number, and email are required")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", body["date_of_birth"]):
        raise util.HttpError(400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD")
    try:
        body["date_of_birth"] = date.fromisoformat(body["date_of_birth"])
    except ValueError as exc:
        raise util.HttpError(400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD") from exc
    body["email"] = body["email"].lower()

    result = ParticipantService().create(body, util.current_user_id(event))
    response: CreateParticipantResponse = {"participant": result["participant"]}
    return util.return_response(201, response)
