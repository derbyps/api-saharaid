import uuid

from shared.configs.config import config
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
        p = params.get("p") or 1
        rp = params.get("rp") or 25

        schedules = self.repo.get_schedules(offset=((p - 1) * rp), limit=rp)
        total_data = self.repo.get_total_data_schedules()

        return GetSchedulesResult(schedules=schedules, total_data=total_data)

    def get_detail(self, schedule_id: str) -> GetDetailScheduleResult:

        schedule = self.repo.get_detail_schedule(schedule_id)
        if not schedule:
            raise NotFound("SCHEDULE_NOT_FOUND")

        return GetDetailScheduleResult(schedule=schedule, documents=[])

    def create(self, body: dict) -> Schedule:

        serial_number = self.repo.get_max_serial_number() + 1

        schedule = Schedule(
            id=uuid.uuid4(),
            course_id=body["course_id"],
            start_date=body["start_date"],
            end_date=body["end_date"],
            location=body["location"],
            course_mode_id=body["course_mode_id"],
            serial_number=serial_number,
            created_at=config.TIMESTAMP,
            created_by=config.USER_ID,
        )

        db.save(schedule)
        db.commit()

        return schedule

    def update(self, schedule_id: str, body: dict) -> Schedule:
        schedule = Schedule.get_detail(schedule_id)
        if not schedule:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        schedule.course_id = body["course_id"]
        schedule.start_date = body["start_date"]
        schedule.end_date = body["end_date"]
        schedule.location = body["location"]
        schedule.course_mode_id = body["course_mode_id"]
        schedule.updated_at = config.TIMESTAMP
        schedule.updated_by = config.USER_ID

        db.commit()

        return schedule
