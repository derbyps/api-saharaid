import json

from shared import util

from ..schemas.participant import DetailParticipantRow
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
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    service = ParticipantService()
    result = service.create(body)
    response: DetailParticipantRow = {
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
    }

    return util.return_response(201, dict(response))
