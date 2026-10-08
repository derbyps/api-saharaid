import uuid

from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import NotFound
from shared.models.schedule import Schedule

from ..repositories.schedule import ScheduleRepository
from ..schemas.event import GetSchedulesParams
from ..schemas.schedule import GetDetailScheduleResult, GetSchedulesResult


class ScheduleService:
    def __init__(self):
        self.repo = ScheduleRepository()

    def get_list(self, params: GetSchedulesParams) -> GetSchedulesResult:
        p = int(params.get("p") or 1)
        rp = int(params.get("rp") or 25)

        schedules = self.repo.get_schedules(offset=((p - 1) * rp), limit=rp)
        total_data = self.repo.get_total_data_schedules()

        return GetSchedulesResult(schedules=schedules, total_data=total_data)

    def get_detail(self, schedule_id: str) -> GetDetailScheduleResult:

        schedule = self.repo.get_detail_schedule(schedule_id)
        if not schedule:
            raise NotFound("SCHEDULE_NOT_FOUND")

        return GetDetailScheduleResult(schedule=schedule, documents=[])

    def create(self, body: dict, actor_id: str) -> Schedule:

        serial_number = self.repo.get_max_serial_number() + 1

        schedule = Schedule(
            course_id=body["course_id"],
            course_class_type_id=body["course_class_type_id"],
            start_date=body["start_date"],
            end_date=body["end_date"],
            location=body["location"],
            serial_number=serial_number,
            batch=body["batch"],
            created_at=config_module.TIMESTAMP,
            created_by=actor_id,
        )

        db.save(schedule)
        db.commit()

        return schedule

    def update(self, schedule_id: str, body: dict, actor_id: str) -> Schedule:
        schedule = Schedule.get_detail(schedule_id)
        if not schedule:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        schedule.course_id = body["course_id"]
        schedule.course_class_type_id = body["course_class_type_id"]
        schedule.start_date = body["start_date"]
        schedule.end_date = body["end_date"]
        schedule.location = body["location"]
        schedule.batch = body["batch"]
        schedule.updated_at = config_module.TIMESTAMP
        schedule.updated_by = actor_id

        db.commit()

        return schedule
