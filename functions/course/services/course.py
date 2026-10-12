import os
import uuid

import uuid_extensions
from botocore.exceptions import BotoCoreError, ClientError

from shared import AWSManager
from shared.configs import config as config_module
from shared.configs.db import db
from shared.exception import BadRequest, Conflict, NotFound
from shared.models.course import Course
from shared.SanityManager import SanityError, SanityManager
from shared.util import HttpError

from ..repositories.course import CourseRepository
from ..schemas.course import CourseResult, PresignCourseResult
from ..schemas.event import CoursePayload, FinalizeBody, PresignBody

MAX_FILE_SIZE = 1024 * 1024
MAX_GALLERY = 6
UPLOAD_URL_TTL_SECONDS = 15 * 60
ALLOWED_TYPES = {
    "gallery": {"image/jpeg", "image/png"},
    "brochure": {"application/pdf"},
}
CONTENT_FIELDS = ("overview", "objective", "outline", "requirement")
MODES = ("online", "offline")


def _key() -> str:
    return uuid.uuid4().hex[:12]


def _ref(ref: str) -> dict:
    return {"_type": "reference", "_ref": ref, "_key": _key()}


def _blocks(blocks: list[dict]) -> list[dict]:
    return [{**block, "_key": block.get("_key") or _key()} for block in blocks]


def _asset_ref(item: dict) -> str:
    return item.get("asset", {}).get("_ref", "")


def _modes(class_type_title: str) -> list[str]:
    """ "Offline/Online" -> ["online", "offline"]; the landing page reads courseMode."""
    parts = {part.strip().lower() for part in class_type_title.split("/")}

    return [mode for mode in MODES if mode in parts]


class CourseService:
    def __init__(self, sanity: SanityManager | None = None, s3=None):
        self.repo = CourseRepository()
        self._sanity = sanity
        self._s3 = s3

    @property
    def sanity(self) -> SanityManager:
        if self._sanity is None:
            self._sanity = SanityManager()

        return self._sanity

    @property
    def s3(self):
        if self._s3 is None:
            self._s3 = AWSManager.S3Manager(os.environ["S3_BUCKET"])

        return self._s3

    def _build_content(
        self, payload: CoursePayload, exclude_id: str | None = None
    ) -> dict:
        """Validate references against MySQL and build the Sanity fields."""
        course_type = self.repo.get_type(payload["course_type_id"])
        class_type = self.repo.get_class_type(payload["course_class_type_id"])
        validity = self.repo.get_certificate_validity(
            payload["course_certificate_validity_id"]
        )
        if not course_type or not class_type or not validity:
            raise BadRequest(
                "INVALID_REFERENCE", "Course type, class type or validity not found"
            )

        sanity_ids = list(dict.fromkeys(payload["theme_sanity_ids"]))
        themes = self.repo.get_themes_by_sanity_ids(sanity_ids)
        if len(themes) != len(sanity_ids):
            raise BadRequest("INVALID_REFERENCE", "Course theme not found")

        related_ids = list(dict.fromkeys(payload["related_course_ids"]))
        if exclude_id in related_ids or len(
            self.repo.get_existing_course_ids(related_ids)
        ) != len(related_ids):
            raise BadRequest("INVALID_REFERENCE", "Related course not found")

        if self.repo.is_slug_taken(payload["slug"], exclude_id):
            raise Conflict("SLUG_TAKEN", "Slug is already used by another course")

        return {
            "themes": themes,
            "related_ids": related_ids,
            "type": course_type,
            "class_type": class_type,
            "validity": validity,
            "fields": {
                "title": payload["title"],
                "slug": {"_type": "slug", "current": payload["slug"]},
                "themes": [_ref(str(theme.sanity_id)) for theme in themes],
                "courseMode": _modes(class_type.title or ""),
                "duration": payload["duration"],
                "certificateValidity": validity.title,
                **{name: _blocks(payload[name]) for name in CONTENT_FIELDS},
                "relatedCourses": [_ref(course_id) for course_id in related_ids],
                "recommendedFor": payload["recommended_for"],
                "courseType": course_type.title,
                "courseTypeCode": course_type.code,
                "courseClassType": class_type.title,
            },
        }

    def create(self, payload: CoursePayload, actor_id: str) -> CourseResult:
        content = self._build_content(payload)
        course_id = str(uuid_extensions.uuid7())

        course = Course(
            sanity_id=course_id,
            course_type_id=payload["course_type_id"],
            course_class_type_id=payload["course_class_type_id"],
            course_certificate_validity_id=payload["course_certificate_validity_id"],
            name=payload["title"],
            asset_status="pending" if payload["has_assets"] else "ready",
            slug=payload["slug"],
            created_at=config_module.get_timestamp(),
            created_by=actor_id,
        )
        course.id = course_id
        db.save(course)
        self.repo.replace_themes(course_id, [theme.id for theme in content["themes"]])
        self.repo.replace_related(course_id, content["related_ids"])

        # Sanity first, commit last: a Sanity failure rolls the DB back.
        try:
            self.sanity.mutate(
                [
                    {
                        "createIfNotExists": {
                            "_id": course_id,
                            "_type": "course",
                            **content["fields"],
                        }
                    }
                ]
            )
        except SanityError as exc:
            raise HttpError(
                502, "SANITY_UNAVAILABLE", "Could not write course to Sanity"
            ) from exc

        try:
            db.commit()
        except Exception:
            self._delete_sanity_doc(course_id)
            raise

        return self._result(course)

    def update(
        self, course_id: str, payload: CoursePayload, actor_id: str
    ) -> CourseResult:
        course = self.repo.get_course(course_id)
        if not course:
            raise NotFound("COURSE_NOT_FOUND", "Course not found")

        content = self._build_content(payload, exclude_id=course_id)
        course.course_type_id = payload["course_type_id"]
        course.course_class_type_id = payload["course_class_type_id"]
        course.course_certificate_validity_id = payload[
            "course_certificate_validity_id"
        ]
        course.name = payload["title"]
        course.slug = payload["slug"]
        course.updated_at = config_module.get_timestamp()
        course.updated_by = actor_id
        if payload["has_assets"]:
            course.asset_status = "pending"
        self.repo.replace_themes(course_id, [theme.id for theme in content["themes"]])
        self.repo.replace_related(course_id, content["related_ids"])

        # ponytail: no compensation if the commit fails after the Sanity patch; retry the PUT.
        try:
            self.sanity.mutate([{"patch": {"id": course_id, "set": content["fields"]}}])
        except SanityError as exc:
            raise HttpError(
                502, "SANITY_UNAVAILABLE", "Could not update course in Sanity"
            ) from exc
        db.commit()

        return self._result(course)

    def presign(self, course_id: str, body: PresignBody) -> PresignCourseResult:
        if not self.repo.get_course(course_id):
            raise NotFound("COURSE_NOT_FOUND", "Course not found")

        files = body["files"]
        galleries = sum(1 for item in files if item["kind"] == "gallery")
        brochures = sum(1 for item in files if item["kind"] == "brochure")
        if not files or galleries > MAX_GALLERY or brochures > 1:
            raise BadRequest(
                "INVALID_FILES", "Provide up to 6 gallery images and 1 brochure"
            )

        uploads = []
        for item in files:
            if item["content_type"] not in ALLOWED_TYPES.get(item["kind"], set()):
                raise BadRequest("INVALID_DOCUMENT", "Unsupported file type")

            key = f"staging/course/{course_id}/{uuid.uuid4().hex}"
            try:
                url = self.s3.generate_presigned_url(
                    "put_object",
                    Params={"Key": key, "ContentType": item["content_type"]},
                    ExpiresIn=UPLOAD_URL_TTL_SECONDS,
                )
            except (BotoCoreError, ClientError) as exc:
                raise HttpError(
                    502, "S3_UNAVAILABLE", "Could not sign upload URL"
                ) from exc
            uploads.append({"s3_key": key, "upload_url": url})

        return PresignCourseResult(files=uploads, expires_in=UPLOAD_URL_TTL_SECONDS)

    def finalize(
        self, course_id: str, body: FinalizeBody, actor_id: str
    ) -> CourseResult:
        course = self.repo.get_course(course_id)
        if not course:
            raise NotFound("COURSE_NOT_FOUND", "Course not found")

        current = self.sanity.query(
            '*[_id == $id][0]{"gallery": coalesce(gallery, []), brochure}',
            {"id": course_id},
        )
        if current is None:
            raise NotFound(
                "SANITY_COURSE_NOT_FOUND", "Course document is missing in Sanity"
            )

        staged: list[str] = []
        patch: dict = {"set": {}, "unset": []}
        replaced_refs: set[str] = set()
        kept_refs: set[str] = set()

        if "gallery" in body:
            keep = {item["_key"]: item for item in current["gallery"] if "_key" in item}
            gallery = []
            for item in body["gallery"]:
                if "key" in item:
                    if item["key"] not in keep:
                        raise BadRequest(
                            "UNKNOWN_GALLERY_ITEM", "Gallery item not found"
                        )
                    gallery.append(keep[item["key"]])
                else:
                    gallery.append(
                        {
                            "_type": "mediaImg",
                            "_key": _key(),
                            "asset": {
                                "_type": "reference",
                                "_ref": self._upload(
                                    item["s3_key"], course_id, "gallery", staged
                                ),
                            },
                        }
                    )
            if len(gallery) > MAX_GALLERY:
                raise BadRequest(
                    "INVALID_FILES", "A course has at most 6 gallery images"
                )
            patch["set"]["gallery"] = gallery
            replaced_refs |= {_asset_ref(item) for item in current["gallery"]}
            kept_refs |= {_asset_ref(item) for item in gallery}

        if "brochure" in body:
            if current.get("brochure"):
                replaced_refs.add(_asset_ref(current["brochure"]))
            if body["brochure"] is None:
                patch["unset"].append("brochure")
            else:
                ref = self._upload(
                    body["brochure"]["s3_key"], course_id, "brochure", staged
                )
                patch["set"]["brochure"] = {
                    "_type": "mediaFile",
                    "asset": {"_type": "reference", "_ref": ref},
                }
                kept_refs.add(ref)

        if patch["set"] or patch["unset"]:
            patch = {"id": course_id, **{k: v for k, v in patch.items() if v}}
            try:
                self.sanity.mutate([{"patch": patch}])
            except SanityError as exc:
                raise HttpError(
                    502, "SANITY_UNAVAILABLE", "Could not update course in Sanity"
                ) from exc

        for asset_id in replaced_refs - kept_refs - {""}:
            self._delete_sanity_doc(asset_id)
        for s3_key in staged:
            try:
                self.s3.delete_object(Key=s3_key)
            except (BotoCoreError, ClientError):
                pass  # staged objects are throwaway; a bucket lifecycle rule can sweep leftovers

        course.asset_status = "ready"
        course.updated_at = config_module.get_timestamp()
        course.updated_by = actor_id
        db.commit()

        return self._result(course)

    def _upload(self, s3_key: str, course_id: str, kind: str, staged: list[str]) -> str:
        """Validate one staged S3 object, then stream it to Sanity. Returns the asset id."""
        if not s3_key.startswith(f"staging/course/{course_id}/"):
            raise BadRequest("INVALID_S3_KEY", "s3_key does not belong to this course")

        try:
            head = self.s3.head_object(Key=s3_key)
        except ClientError as exc:
            raise NotFound("ASSET_NOT_FOUND", "Uploaded file not found") from exc

        if head["ContentType"] not in ALLOWED_TYPES[kind]:
            raise BadRequest("INVALID_DOCUMENT", "Unsupported file type")
        if not 0 < head["ContentLength"] <= MAX_FILE_SIZE:
            raise BadRequest("INVALID_DOCUMENT", "Each file must be at most 1 MiB")

        staged.append(s3_key)
        body = self.s3.get_object(Key=s3_key)["Body"]
        try:
            return self.sanity.upload_asset(
                "image" if kind == "gallery" else "file",
                body,
                s3_key.rsplit("/", 1)[-1],
                head["ContentType"],
                head["ContentLength"],
            )
        except SanityError as exc:
            raise HttpError(
                502, "SANITY_UNAVAILABLE", "Could not upload asset to Sanity"
            ) from exc

    def _delete_sanity_doc(self, doc_id: str) -> None:
        try:
            self.sanity.mutate([{"delete": {"id": doc_id}}])
        except SanityError:
            pass  # still referenced elsewhere or already gone; harmless

    @staticmethod
    def _result(course: Course) -> CourseResult:
        return CourseResult(
            id=course.id,
            sanity_id=course.sanity_id,
            title=course.name,
            asset_status=course.asset_status,
        )
