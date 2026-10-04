from shared import util

from ..schemas.event import GetParticipantsParams
from ..schemas.participant import GetDetailParticipantResult
from ..schemas.response import PaginatedParticipantsResponse
from ..services.participant import ParticipantService
from ..services.upload import UploadService


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


def download_participants_handler(event: dict) -> dict:

    params: GetParticipantsParams = event.get("queryStringParameters") or {}

    participant_service = ParticipantService()
    download_service = UploadService()
    data_export = participant_service.download(params)
    download_url = download_service.to_s3(data_export)

    return util.return_response(200, {"url_report": download_url})


def get_participant_detail_handler(event: dict) -> dict:
    participant_id = (event.get("pathParameters") or {}).get("id")
    if not participant_id:
        raise util.HttpError(400, "INVALID_ID", "id is required")
    util.current_user_id(event)

    service = ParticipantService()
    result = service.get_detail(participant_id)

    response: GetDetailParticipantResult = {
        "participant": result["participant"],
        "documents": result["documents"],
    }

    return util.return_response(200, dict(response))
