import json

from shared import util

from ..schemas.enrollment import DetailEnrollmentRow
from ..services.enrollment import EnrollmentService


def create_enrollment_handler(event: dict) -> dict:
    body = json.loads(event.get("body") or "{}")
    req_body = [
        "schedule_id",
        "participant_ids",
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    service = EnrollmentService()
    result = service.create(body)
    response: DetailEnrollmentRow = {"id": str(result.id)}

    return util.return_response(201, dict(response))
