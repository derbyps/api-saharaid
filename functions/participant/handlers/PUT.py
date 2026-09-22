import json
import uuid

from shared import util
from shared.configs.config import config
from shared.configs.db import db
from shared.models.participant import Participant


def update_participant_handler(event: dict) -> dict:
    participant_id = (event.get("pathParameters") or {}).get("id")
    if not participant_id:
        return util.return_response(400, {})

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

    participant = Participant.get_detail(participant_id)
    if not participant:
        return util.return_response(404, {})

    participant.name = body["name"]
    participant.identity_number = body["identity_number"]
    participant.gender = body["gender"]
    participant.phone_number = body["phone_number"]
    participant.email = body["email"]
    participant.date_of_birth = body["date_of_birth"]
    participant.religion = body["religion"]
    participant.address = body["address"]
    participant.job_position = body["job_position"]
    participant.job_company = body["job_company"]
    participant.education = body["education"]
    participant.cr_number = body["cr_number"]

    db.commit()

    return util.return_response(201, {})
