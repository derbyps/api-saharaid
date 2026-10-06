import os
from datetime import timedelta

import boto3

from shared import util
from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import NotFound
from shared.helpers.utils import get_s3_signed_url
from shared.models.instructor import Instructor

from ..repositories.document import DocumentRepository
from ..repositories.instructor import InstructorRepository, InstructorRow
from ..schemas.document import DocumentsRow
from ..schemas.event import GetInstructorsParams
from ..schemas.instructor import GetDetailInstructorResult, GetInstructorsResult


class InstructorService:
    def __init__(self):
        self.instructor_repo = InstructorRepository()
        self.document_repo = DocumentRepository()

    def get_list(self, params: GetInstructorsParams) -> GetInstructorsResult:
        query = self.instructor_repo.generate_get_instructors(params)
        rows = self.instructor_repo.get_instructors(params, query)
        total_data = self.instructor_repo.get_total_data_instructors(query)

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

        instructor = self.instructor_repo.get_detail_instructor(instructor_id)
        if not instructor:
            raise NotFound("INSTRUCTOR_NOT_FOUND")

        documents_row = self.document_repo.get_documents(instructor_id)
        session = boto3.Session(region_name=os.getenv("REGION"))
        s3_client = session.client("s3")
        documents: list[DocumentsRow] = []
        for row in documents_row:
            url = None
            if row.get("s3_key"):
                url = get_s3_signed_url(
                    s3_client, row.get("s3_key") or "", timedelta(days=1)
                )

            documents.append(
                DocumentsRow(
                    id=row["id"],
                    owner_id=row["owner_id"],
                    owner_type=row["owner_type"],
                    document_type=row["document_type"],
                    s3_key=url,
                    content_type=row["content_type"],
                )
            )

        return GetDetailInstructorResult(instructor=instructor, documents=documents)

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
        return instructor

    def delete(self, instructor_id: str, event: dict) -> Instructor:
        params = event.get("queryStringParameters") or {}

        instructor = Instructor.get_detail(instructor_id)
        if not instructor:
            raise NotFound("INSTRUCTOR_NOT_FOUND")

        if params.get("origin") == "creation":
            self.instructor_repo.hard_delete(instructor_id)
            db.commit()
            return instructor

        actor_id = util.current_user_id(event)
        instructor.is_deleted = True
        instructor.deleted_at = config_module.TIMESTAMP
        instructor.deleted_by = str(actor_id)

        db.commit()

        return instructor
