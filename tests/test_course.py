"""Sandbox tests: in-memory SQLite, fake Sanity and S3. Nothing touches real services."""

import io
import json
import unittest
from datetime import datetime
from typing import Any, cast
from unittest.mock import patch

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from functions.course.lambda_function import lambda_handler
from functions.course.services.course import CourseService
from shared.configs.db import Base, db
from shared.exception import BadRequest, Conflict, NotFound
from shared.models.course import Course
from shared.models.course_certificate_validity import CourseCertificateValidity
from shared.models.course_class_type import CourseClassType
from shared.models.course_theme import CourseTheme
from shared.models.course_theme_detail import CourseThemeDetail
from shared.models.course_type import CourseType
from shared.SanityManager import SanityError
from shared.util import HttpError

BLOCK = {"_type": "block", "children": [{"_type": "span", "text": "hi"}]}


class FakeSanity:
    def __init__(self):
        self.mutations: list[dict] = []
        self.docs: dict[str, dict] = {}
        self.fail = False

    def mutate(self, mutations):
        if self.fail:
            raise SanityError(500, "boom")
        self.mutations += mutations

    def query(self, groq, params=None):
        return self.docs.get((params or {})["id"])

    def upload_asset(self, kind, body, filename, content_type, content_length):
        data = body.read()
        assert len(data) == content_length
        return f"{kind}-{len(data)}-{filename}"


class FakeS3:
    def __init__(self):
        self.objects: dict[str, tuple[bytes, str]] = {}

    def generate_presigned_url(self, method, Params, ExpiresIn):
        return f"https://s3.test/{Params['Key']}?type={Params['ContentType']}"

    def head_object(self, Key):
        from botocore.exceptions import ClientError

        if Key not in self.objects:
            raise ClientError({"Error": {"Code": "404"}}, "HeadObject")
        data, content_type = self.objects[Key]
        return {"ContentLength": len(data), "ContentType": content_type}

    def get_object(self, Key):
        return {"Body": io.BytesIO(self.objects[Key][0])}

    def delete_object(self, Key):
        self.objects.pop(Key, None)


def payload(**changes):
    return {
        "title": "Well Control",
        "slug": "well-control",
        "theme_sanity_ids": ["theme-sanity-1"],
        "course_type_id": "type-1",
        "course_class_type_id": "class-both",
        "course_certificate_validity_id": "validity-1",
        "duration": "4 Days",
        "overview": [BLOCK],
        "objective": [],
        "outline": [],
        "requirement": [],
        "related_course_ids": [],
        "recommended_for": ["student"],
        "has_assets": True,
        **changes,
    }


class CourseServiceTest(unittest.TestCase):
    def setUp(self):
        engine = create_engine(
            "sqlite://", poolclass=StaticPool, connect_args={"check_same_thread": False}
        )
        Base.metadata.create_all(engine)
        db._session = sessionmaker(engine, expire_on_commit=False)()
        db.session.add_all(
            [
                CourseType(
                    sanity_id=None,
                    title="Training",
                    code="II",
                    synced_at=None,
                    created_at=None,
                    created_by=None,
                ),
                CourseClassType(
                    sanity_id=None,
                    title="Offline/Online",
                    synced_at=None,
                    created_at=None,
                    created_by=None,
                ),
                CourseCertificateValidity(
                    sanity_id=None,
                    title="1 Year",
                    synced_at=None,
                    created_at=None,
                    created_by=None,
                ),
                CourseTheme(
                    sanity_id="theme-sanity-1",
                    title="Drilling",
                    slug="drilling",
                    synced_at=None,
                    created_at=None,
                    created_by=None,
                ),
            ]
        )
        db.session.flush()
        self.ids = {
            "type": db.session.scalar(select(CourseType.id)),
            "class": db.session.scalar(select(CourseClassType.id)),
            "validity": db.session.scalar(select(CourseCertificateValidity.id)),
            "theme": db.session.scalar(select(CourseTheme.id)),
        }
        db.commit()

        patcher = patch(
            "shared.configs.config.get_timestamp", lambda *_: datetime(2026, 10, 11)
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self.addCleanup(lambda: setattr(db, "_session", None))

        self.sanity, self.s3 = FakeSanity(), FakeS3()
        self.service = CourseService(sanity=cast(Any, self.sanity), s3=self.s3)

    def payload(self, **changes):
        return payload(
            course_type_id=self.ids["type"],
            course_class_type_id=self.ids["class"],
            course_certificate_validity_id=self.ids["validity"],
            **changes,
        )

    def test_create_writes_sanity_and_db(self):
        result = self.service.create(self.payload(), "actor")

        self.assertEqual(result["id"], result["sanity_id"])
        self.assertEqual(result["asset_status"], "pending")
        mutation = self.sanity.mutations[0]["createIfNotExists"]
        self.assertEqual(mutation["_id"], result["id"])
        self.assertEqual(mutation["courseMode"], ["online", "offline"])
        self.assertEqual(mutation["certificateValidity"], "1 Year")
        self.assertEqual(
            (
                mutation["courseType"],
                mutation["courseTypeCode"],
                mutation["courseClassType"],
            ),
            ("Training", "II", "Offline/Online"),
        )
        self.assertEqual(mutation["themes"][0]["_ref"], "theme-sanity-1")
        self.assertTrue(mutation["themes"][0]["_key"])
        self.assertTrue(mutation["overview"][0]["_key"])
        details = db.session.scalars(select(CourseThemeDetail)).all()
        self.assertEqual([d.course_theme_id for d in details], [self.ids["theme"]])

    def test_create_without_assets_is_ready(self):
        self.assertEqual(
            self.service.create(self.payload(has_assets=False), "a")["asset_status"],
            "ready",
        )

    def test_sanity_failure_leaves_no_row(self):
        self.sanity.fail = True
        with self.assertRaises(HttpError):
            self.service.create(self.payload(), "actor")
        db.session.rollback()  # what handle_errors' db.close() does
        self.assertEqual(db.session.scalars(select(Course)).all(), [])

    def test_rejects_bad_references_and_duplicate_slug(self):
        with self.assertRaises(BadRequest):
            self.service.create(self.payload(theme_sanity_ids=["missing"]), "a")
        with self.assertRaises(BadRequest):
            self.service.create(self.payload(related_course_ids=["missing"]), "a")
        self.service.create(self.payload(), "a")
        with self.assertRaises(Conflict):
            self.service.create(self.payload(), "a")

    def test_update_patches_fields_without_touching_assets(self):
        course_id = self.service.create(self.payload(), "a")["id"]
        self.service.update(course_id, self.payload(title="New", has_assets=False), "a")

        patch_mutation = self.sanity.mutations[-1]["patch"]
        self.assertEqual(patch_mutation["id"], course_id)
        self.assertEqual(patch_mutation["set"]["title"], "New")
        self.assertNotIn("gallery", patch_mutation["set"])
        self.assertNotIn("brochure", patch_mutation["set"])
        with self.assertRaises(BadRequest):  # a course cannot relate to itself
            self.service.update(
                course_id, self.payload(related_course_ids=[course_id]), "a"
            )
        with self.assertRaises(NotFound):
            self.service.update("nope", self.payload(), "a")

    def test_presign_uses_staging_keys(self):
        course_id = self.service.create(self.payload(), "a")["id"]
        files: Any = [
            {"kind": "gallery", "content_type": "image/png"},
            {"kind": "brochure", "content_type": "application/pdf"},
        ]
        signed = self.service.presign(course_id, {"files": files})

        keys = [f["s3_key"] for f in signed["files"]]
        self.assertTrue(all(k.startswith(f"staging/course/{course_id}/") for k in keys))
        self.assertEqual(len(set(keys)), 2)
        with self.assertRaises(BadRequest):
            self.service.presign(
                course_id,
                cast(
                    Any,
                    {"files": [{"kind": "gallery", "content_type": "application/pdf"}]},
                ),
            )
        with self.assertRaises(BadRequest):
            self.service.presign(
                course_id,
                cast(
                    Any,
                    {"files": [{"kind": "gallery", "content_type": "image/png"}] * 7},
                ),
            )

    def _stage(self, course_id, name, data=b"x" * 10, content_type="image/png"):
        key = f"staging/course/{course_id}/{name}"
        self.s3.objects[key] = (data, content_type)
        return key

    def test_finalize_streams_assets_and_replaces_gallery(self):
        course_id = self.service.create(self.payload(), "a")["id"]
        old_image = {
            "_key": "k1",
            "_type": "mediaImg",
            "alt": "keep me",
            "asset": {"_type": "reference", "_ref": "image-old-keep"},
        }
        dropped = {
            "_key": "k2",
            "_type": "mediaImg",
            "asset": {"_type": "reference", "_ref": "image-old-drop"},
        }
        self.sanity.docs[course_id] = {
            "gallery": [old_image, dropped],
            "brochure": {
                "_type": "mediaFile",
                "asset": {"_type": "reference", "_ref": "file-old"},
            },
        }
        new_image = self._stage(course_id, "img")
        pdf = self._stage(course_id, "pdf", content_type="application/pdf")

        result = self.service.finalize(
            course_id,
            {
                "gallery": [{"s3_key": new_image}, {"key": "k1"}],
                "brochure": {"s3_key": pdf},
            },
            "a",
        )

        self.assertEqual(result["asset_status"], "ready")
        patch_mutation = next(m["patch"] for m in self.sanity.mutations if "patch" in m)
        gallery = patch_mutation["set"]["gallery"]
        self.assertEqual(gallery[0]["asset"]["_ref"], "image-10-img")
        self.assertEqual(gallery[1], old_image)  # kept item, alt text intact
        self.assertEqual(
            patch_mutation["set"]["brochure"]["asset"]["_ref"], "file-10-pdf"
        )
        deleted = {m["delete"]["id"] for m in self.sanity.mutations if "delete" in m}
        self.assertEqual(deleted, {"image-old-drop", "file-old"})
        self.assertEqual(self.s3.objects, {})

    def test_finalize_brochure_null_unsets(self):
        course_id = self.service.create(self.payload(), "a")["id"]
        self.sanity.docs[course_id] = {"gallery": [], "brochure": None}
        self.service.finalize(course_id, {"brochure": None}, "a")
        self.assertEqual(self.sanity.mutations[-1]["patch"]["unset"], ["brochure"])

    def test_finalize_rejects_bad_files(self):
        course_id = self.service.create(self.payload(), "a")["id"]
        self.sanity.docs[course_id] = {"gallery": [], "brochure": None}
        big = self._stage(course_id, "big", data=b"x" * (1024 * 1024 + 1))
        wrong = self._stage(course_id, "wrong", content_type="application/pdf")
        for body, error in (
            ({"gallery": [{"s3_key": big}]}, BadRequest),
            ({"gallery": [{"s3_key": wrong}]}, BadRequest),
            ({"gallery": [{"s3_key": "staging/course/other/x"}]}, BadRequest),
            ({"gallery": [{"s3_key": f"staging/course/{course_id}/absent"}]}, NotFound),
            ({"gallery": [{"key": "unknown"}]}, BadRequest),
        ):
            with self.assertRaises(error):
                self.service.finalize(course_id, cast(Any, body), "a")
        self.assertEqual(db.session.scalar(select(Course.asset_status)), "pending")


class CourseRouteTest(unittest.TestCase):
    def test_create_route_returns_201_and_validates(self):
        def call(body):
            event = {
                "requestContext": {"http": {"method": "POST"}},
                "rawPath": "/course",
                "body": json.dumps(body),
            }
            with (
                patch.object(db, "open"),
                patch.object(db, "close"),
                patch(
                    "functions.course.handlers.POST.util.current_user_id",
                    return_value="actor",
                ),
                patch("functions.course.handlers.POST.CourseService") as service,
            ):
                service.return_value.create.return_value = {
                    "id": "1",
                    "sanity_id": "1",
                    "title": "t",
                    "asset_status": "ready",
                }
                response = lambda_handler(event, None)
            return response["statusCode"], json.loads(response["body"])

        status, body = call(payload(has_assets=False))
        self.assertEqual((status, body["course"]["id"]), (201, "1"))
        status, body = call(payload(overview=["not a block"]))
        self.assertEqual((status, body["errCode"]), (400, "INVALID_COURSE"))


if __name__ == "__main__":
    unittest.main()
