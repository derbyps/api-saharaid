from shared import util

from ..schemas.participant import GetDetailParticipantResult
from ..services.course_history import CourseHistoryService


def get_detail_method_handler(event: dict) -> dict:
    participant_id = (event.get("pathParameters") or {}).get("id")
    if not participant_id:
        return util.return_response(400, {})

    service = CourseHistoryService()
    result = service.get_detail(participant_id)

    response: GetDetailParticipantResult = {
        "participant": result["participant"],
        "documents": result["documents"],
    }

    return util.return_response(200, dict(response))
