import re
from datetime import date

from shared import util

from ..schemas.event import CreateParticipantBody
from ..schemas.participant import DetailParticipantRow
from ..schemas.response import CreateParticipantResponse
from ..services.participant import ParticipantService


def create_participant_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = [
        "name",
        "identity_number",
        "gender",
        "phone_number",
        "email",
        "date_of_birth",
        "religion",
        "address",
        "job_position",
        "job_company",
        "education",
        "cr_number",
        "tax_number",
        "serial_number",
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    for field in ("name", "phone_number", "email"):
        body[field] = body[field].strip()
        if not body[field]:
            raise util.HttpError(400, "INVALID_BODY", f"{field} is required")

    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", body["date_of_birth"]):
        raise util.HttpError(400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD")
    try:
        body["date_of_birth"] = date.fromisoformat(body["date_of_birth"])
    except ValueError as exc:
        raise util.HttpError(
            400, "INVALID_BODY", "date_of_birth must be YYYY-MM-DD"
        ) from exc

    actor_id = util.current_user_id(event)
    result = ParticipantService().create(body, str(actor_id))

    participant: DetailParticipantRow = {
        "id": str(result.id),
        "name": result.name,
        "identity_number": result.identity_number,
        "gender": result.gender,
        "phone_number": result.phone_number,
        "email": result.email,
        "date_of_birth": result.date_of_birth,
        "religion": result.religion,
        "address": result.address,
        "job_position": result.job_position,
        "job_company": result.job_company,
        "education": result.education,
        "cr_number": result.cr_number,
        "tax_number": result.tax_number,
        "serial_number": result.serial_number,
        "created_at": result.created_at,
        "updated_at": None,
    }
    response: CreateParticipantResponse = {"participant": participant}

    return util.return_response(201, dict(response))
