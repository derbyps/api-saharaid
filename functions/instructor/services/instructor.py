from shared.configs import config as config_module
from shared.configs.config import config
from shared.configs.db import db
from shared.exception import NotFound
from shared.models.instructor import Instructor

from ..repositories.instructor import InstructorRepository
from ..schemas.event import GetInstructorsParams
from ..schemas.instructor import GetDetailInstructorResult, GetInstructorsResult


class InstructorService:
    def __init__(self):
        self.repo = InstructorRepository()

    def get_list(self, params: GetInstructorsParams) -> GetInstructorsResult:
        query = self.repo.generate_get_instructors(params)
        instructors = self.repo.get_instructors(params, query)
        total_data = self.repo.get_total_data_instructors(query)

        return GetInstructorsResult(instructors=instructors, total_data=total_data)

    def get_detail(self, instructor_id: str) -> GetDetailInstructorResult:

        instructor = self.repo.get_detail_instructor(instructor_id)
        if not instructor:
            raise NotFound("INSTRUCTOR_NOT_FOUND")

        return GetDetailInstructorResult(instructor=instructor, documents=[])

    def create(self, body: dict) -> Instructor:
        instructor = Instructor(
            name=body["name"],
            email=body["email"],
            phone_number=body["phone_number"],
            course_theme_id=body["course_theme_id"],
            specialization=body["specialization"],
            created_at=config_module.TIMESTAMP,
            created_by=config_module.USER_ID,
        )

        db.save(instructor)
        db.commit()

        return instructor

    def update(self, instructor_id: str, body: dict) -> Instructor:
        instructor = Instructor.get_detail(instructor_id)
        if not instructor:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        instructor.name = body["name"]
        instructor.phone_number = body["phone_number"]
        instructor.course_theme_id = body["course_theme_id"]
        instructor.specialization = body["specialization"]
        instructor.updated_at = config_module.TIMESTAMP
        instructor.updated_by = config_module.USER_ID

        db.commit()

        return instructor
