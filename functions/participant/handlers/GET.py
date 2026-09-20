from shared import util

from ..schemas.event import GetParticipantsParams
from ..schemas.participant import GetDetailParticipantResult
from ..schemas.response import PaginatedParticipantsResponse
from ..services.participant import ParticipantService


def get_participants_handler(event: dict) -> dict:

    params: GetParticipantsParams = event.get("queryStringParameters") or {}

    service = ParticipantService()
    result = service.get_list(params)

    response: PaginatedParticipantsResponse = {
        "participants": result["participants"],
        "metadata": {
            "p": params.get("p") or 1,
            "rp": params.get("rp") or 25,
            "total_data": result["total_data"],
        },
    }

    return util.return_response(200, dict(response))


def get_participant_detail_handler(event: dict) -> dict:

    service = ParticipantService()
    result = service.get_detail()

    response: GetDetailParticipantResult = {
        "participant": result["participant"],
        "documents": result["documents"],
    }

    return util.return_response(200, dict(response))
