from shared import util
from shared.exception import BadRequest

from ..schemas.event import CreateEnrollmentBody
from ..schemas.response import CreateEnrollmentResponse
from ..services.enrollment import EnrollmentService

MAX_PARTICIPANTS = 200


def _parse_body(event: dict) -> CreateEnrollmentBody:
    body = util.parse_body(event)

    schedule_id = body.get("schedule_id")
    if not isinstance(schedule_id, str) or not schedule_id.strip():
        raise BadRequest("INVALID_ENROLLMENT", "schedule_id is required")

    raw_ids = body.get("participant_ids")
    if not isinstance(raw_ids, list) or not raw_ids:
        raise BadRequest(
            "INVALID_ENROLLMENT", "participant_ids must be a non-empty list of ids"
        )

    participant_ids: list[str] = []
    for item in raw_ids:
        if not isinstance(item, str) or not item.strip():
            raise BadRequest(
                "INVALID_ENROLLMENT", "participant_ids must be a non-empty list of ids"
            )
        participant_ids.append(item)

    unique_ids = list(dict.fromkeys(participant_ids))
    if len(unique_ids) > MAX_PARTICIPANTS:
        raise BadRequest(
            "INVALID_ENROLLMENT",
            f"At most {MAX_PARTICIPANTS} participants can be enrolled at once",
        )

    return CreateEnrollmentBody(schedule_id=schedule_id, participant_ids=unique_ids)


def create_enrollment_handler(event: dict) -> dict:
    body = _parse_body(event)
    actor_id = util.current_user_id(event)

    result = EnrollmentService().create(body, str(actor_id))
    response: CreateEnrollmentResponse = {"inserted": result["inserted"]}

    return util.return_response(201, dict(response))
