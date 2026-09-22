import json
import uuid

from shared import util
from shared.configs.config import config
from shared.configs.db import db
from shared.models.participant import Participant


def delete_method_handler(event: dict) -> dict:
    participant_id = (event.get("pathParameters") or {}).get("id")
    if not participant_id:
        return util.return_response(400, {})

    participant = Participant.get_detail(participant_id)
    if not participant:
        return util.return_response(404, {})

    participant.is_deleted = True
    participant.deleted_at = config.TIMESTAMP
    participant.deleted_by = config.USER_ID

    db.commit()

    return util.return_response(200, {})
