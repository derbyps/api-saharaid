import json

from shared import util

from ..schemas.instructor import DetailInstructorRow
from ..services.instructor import InstructorService


def create_instructor_handler(event: dict) -> dict:
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
    result = service.create(body)
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
