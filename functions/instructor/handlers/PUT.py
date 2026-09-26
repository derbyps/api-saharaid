import json

from shared import util

from ..schemas.instructor import DetailInstructorRow
from ..services.instructor import InstructorService


def update_instructor_handler(event: dict) -> dict:
    instructor_id = (event.get("pathParameters") or {}).get("id")
    if not instructor_id:
        return util.return_response(400, {})

    body = json.loads(event.get("body") or "{}")
    req_body = [
        "name",
        "phone_number",
        "email",
        "course_theme_id",
        "specialization",
    ]
    for item in req_body:
        if item not in body:
            return util.return_response(422, {})

    service = InstructorService()
    result = service.update(instructor_id, body)
    response: DetailInstructorRow = {
        "id": str(result.id),
        "name": result.name,
        "phone_number": result.phone_number,
        "email": result.email,
        "course_theme_id": str(result.course_theme_id),
        "specialization": result.specialization,
        "created_at": result.created_at,
    }

    return util.return_response(201, dict(response))
