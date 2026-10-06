from shared import util

from ..services.instructor import InstructorService


def delete_method_handler(event: dict) -> dict:
    instructor_id = (event.get("pathParameters") or {}).get("id")
    if not instructor_id:
        return util.return_response(400, {})

    service = InstructorService()
    instructor = service.delete(instructor_id, event)

    return util.return_response(
        200,
        {
            "instructor": {
                "id": instructor.id,
                "name": instructor.name,
                "phone_number": instructor.phone_number,
                "email": instructor.email,
                "course_theme_id": str(instructor.course_theme_id),
                "specialization": instructor.specialization,
                "created_at": instructor.created_at,
            }
        },
    )
