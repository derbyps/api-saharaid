from shared import util
from shared.configs.config import config
from shared.configs.db import db
from shared.models.instructor import Instructor


def delete_method_handler(event: dict) -> dict:
    instructor_id = (event.get("pathParameters") or {}).get("id")
    if not instructor_id:
        return util.return_response(400, {})

    instructor = Instructor.get_detail(instructor_id)
    if not instructor:
        return util.return_response(404, {})

    instructor.is_deleted = True
    instructor.deleted_at = config.TIMESTAMP
    instructor.deleted_by = config.USER_ID

    db.commit()

    return util.return_response(200, {})
