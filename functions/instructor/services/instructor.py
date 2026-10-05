import os
from datetime import timedelta

import boto3

from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import NotFound
from shared.helpers.utils import get_s3_signed_url
from shared.models.instructor import Instructor

from ..repositories.instructor import InstructorRepository, InstructorRow
from ..schemas.event import GetInstructorsParams
from ..schemas.instructor import GetDetailInstructorResult, GetInstructorsResult


class InstructorService:
    def __init__(self):
        self.repo = InstructorRepository()

    def get_list(self, params: GetInstructorsParams) -> GetInstructorsResult:
        query = self.repo.generate_get_instructors(params)
        rows = self.repo.get_instructors(params, query)
        total_data = self.repo.get_total_data_instructors(query)

        session = boto3.Session(region_name=os.getenv("REGION"))
        s3_client = session.client("s3")

        instructors: list[InstructorRow] = []
        for row in rows:
            passport_photo = None
            if row.get("passport_photo"):
                passport_photo = get_s3_signed_url(
                    s3_client, row.get("passport_photo") or "", timedelta(days=1)
                )

            cv = None
            if row.get("cv"):
                cv = get_s3_signed_url(
                    s3_client, row.get("cv") or "", timedelta(days=1)
                )

            instructors.append(
                InstructorRow(
                    id=row["id"],
                    name=row["name"],
                    phone_number=row["phone_number"],
                    email=row["email"],
                    course_theme_id=row["course_theme_id"],
                    specialization=row["specialization"],
                    created_at=row["created_at"],
                    created_by=row["created_by"],
                    passport_photo=passport_photo,
                    cv=cv,
                )
            )

        return GetInstructorsResult(instructors=instructors, total_data=total_data)

    def get_detail(self, instructor_id: str) -> GetDetailInstructorResult:

        instructor = self.repo.get_detail_instructor(instructor_id)
        if not instructor:
            raise NotFound("INSTRUCTOR_NOT_FOUND")

        return GetDetailInstructorResult(instructor=instructor, documents=[])

    def create(self, body: dict, actor_id: str) -> Instructor:
        instructor = Instructor(
            name=body["name"],
            email=body["email"],
            phone_number=body["phone_number"],
            course_theme_id=body["course_theme_id"],
            specialization=body["specialization"],
            created_at=config_module.TIMESTAMP,
            created_by=actor_id,
        )

        db.save(instructor)
        db.commit()

        return instructor

    def update(self, instructor_id: str, body: dict, actor_id: str) -> Instructor:
        instructor = Instructor.get_detail(instructor_id)
        if not instructor:
            raise NotFound("PARTICIPANT_NOT_FOUND")

        instructor.name = body["name"]
        instructor.phone_number = body["phone_number"]
        instructor.course_theme_id = body["course_theme_id"]
        instructor.specialization = body["specialization"]
        instructor.updated_at = config_module.TIMESTAMP
        instructor.updated_by = actor_id

        db.commit()

        return instructor

        return instructor
