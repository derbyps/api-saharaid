from shared import util
from shared.configs.config import config
from shared.configs.db import db
from shared.models.schedule import Schedule


def delete_method_handler(event: dict) -> dict:
    schedule_id = (event.get("pathParameters") or {}).get("id")
    if not schedule_id:
        return util.return_response(400, {})

    schedule = Schedule.get_detail(schedule_id)
    if not schedule:
        return util.return_response(404, {})

    schedule.is_deleted = True
    schedule.deleted_at = config.TIMESTAMP
    schedule.deleted_by = config.USER_ID

    db.commit()

    return util.return_response(200, {})
