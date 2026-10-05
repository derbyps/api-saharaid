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

    actor_id = util.current_user_id(event)
    service = ParticipantService()
    result = service.create(body, str(actor_id))
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

    return util.return_response(201, {"participant": dict(response)})


def import_participant_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = ["data", "headers"]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    actor_id = util.current_user_id(event)
    service = ParticipantService()
    result = service.bulk(body, str(actor_id))

    participants = [
        {
            "id": participant.id,
            "name": participant.name,
            "identity_number": participant.identity_number,
            "gender": participant.gender,
            "phone_number": participant.phone_number,
            "email": participant.email,
            "date_of_birth": participant.date_of_birth,
            "religion": participant.religion,
            "address": participant.address,
            "job_position": participant.job_position,
            "job_company": participant.job_company,
            "education": participant.education,
            "cr_number": participant.cr_number,
            "tax_number": participant.tax_number,
            "serial_number": participant.serial_number,
        }
        for participant in result
    ]

    return util.return_response(201, {"participants": participants})
