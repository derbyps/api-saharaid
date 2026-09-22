import json
import uuid

from shared import util
from shared.configs.config import config
from shared.configs.db import db
from shared.models.participant import Participant


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

    participant = Participant(
        id=uuid.uuid4(),
        name=body["name"],
        identity_number=body["identity_number"],
        gender=body["gender"],
        phone_number=body["phone_number"],
        email=body["email"],
        date_of_birth=body["date_of_birth"],
        religion=body["religion"],
        address=body["address"],
        job_position=body["job_position"],
        job_company=body["job_company"],
        education=body["education"],
        cr_number=body["cr_number"],
        tax_number=body["tax_number"],
        serial_number=body["serial_number"],
        created_at=config.TIMESTAMP,
        created_by=config.USER_ID,
    )

    db.save(participant)
    db.commit()

    return util.return_response(201, {})
