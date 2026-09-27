from shared import util

from ..schemas.event import GetEnrollmentsParams
from ..schemas.response import PaginatedEnrollmentsResponse
from ..services.enrollment import EnrollmentService


def get_enrollments_handler(event: dict) -> dict:

    params: GetEnrollmentsParams = event.get("queryStringParameters") or {}

    service = EnrollmentService()
    result = service.get_list(params)

    response: PaginatedEnrollmentsResponse = {
        "enrollments": result["enrollments"],
        "metadata": {
            "p": params.get("p") or 1,
            "rp": params.get("rp") or 25,
            "total_data": result["total_data"],
        },
    }

    return util.return_response(200, dict(response))
