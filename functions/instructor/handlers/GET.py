from shared import util

from ..schemas.event import GetInstructorsParams
from ..schemas.instructor import GetDetailInstructorResult
from ..schemas.response import PaginatedInstructorsResponse
from ..services.instructor import InstructorService


def get_instructors_handler(event: dict) -> dict:

    params: GetInstructorsParams = event.get("queryStringParameters") or {}

    service = InstructorService()
    result = service.get_list(params)

    response: PaginatedInstructorsResponse = {
        "instructors": result["instructors"],
        "metadata": {
            "p": params.get("p") or 1,
            "rp": params.get("rp") or 25,
            "total_data": result["total_data"],
        },
    }

    return util.return_response(200, dict(response))


def get_instructor_detail_handler(event: dict) -> dict:
    instructor_id = (event.get("pathParameters") or {}).get("id")
    if not instructor_id:
        return util.return_response(400, {})

    service = InstructorService()
    result = service.get_detail(instructor_id)

    response: GetDetailInstructorResult = {
        "instructor": result["instructor"],
        "documents": result["documents"],
    }

    return util.return_response(200, dict(response))
