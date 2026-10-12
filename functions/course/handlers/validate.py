from shared import util
from shared.exception import BadRequest

from ..schemas.event import CoursePayload, FinalizeBody, PresignBody

RECOMMENDED_FOR = {"fresh-graduate", "experienced", "student"}


def _strings(value, name: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        raise BadRequest("INVALID_COURSE", f"{name} must be a list of strings")

    return value


def _blocks(value, name: str) -> list[dict]:
    if not isinstance(value, list) or not all(
        isinstance(item, dict) and item.get("_type") == "block" for item in value
    ):
        raise BadRequest(
            "INVALID_COURSE", f"{name} must be a list of portable text blocks"
        )

    return value


def parse_course_payload(event: dict) -> CoursePayload:
    body = util.parse_body(event)

    for name in (
        "title",
        "slug",
        "course_type_id",
        "course_class_type_id",
        "course_certificate_validity_id",
    ):
        if not isinstance(body.get(name), str) or not body[name].strip():
            raise BadRequest("INVALID_COURSE", f"{name} is required")

    recommended_for = _strings(body.get("recommended_for", []), "recommended_for")
    if not set(recommended_for) <= RECOMMENDED_FOR:
        raise BadRequest("INVALID_COURSE", "recommended_for has an unknown value")

    duration = body.get("duration", "")
    if not isinstance(duration, str):
        raise BadRequest("INVALID_COURSE", "duration must be a string")

    return CoursePayload(
        title=body["title"].strip(),
        slug=body["slug"].strip(),
        theme_sanity_ids=_strings(body.get("theme_sanity_ids", []), "theme_sanity_ids"),
        course_type_id=body["course_type_id"],
        course_class_type_id=body["course_class_type_id"],
        course_certificate_validity_id=body["course_certificate_validity_id"],
        duration=duration.strip(),
        overview=_blocks(body.get("overview", []), "overview"),
        objective=_blocks(body.get("objective", []), "objective"),
        outline=_blocks(body.get("outline", []), "outline"),
        requirement=_blocks(body.get("requirement", []), "requirement"),
        related_course_ids=_strings(
            body.get("related_course_ids", []), "related_course_ids"
        ),
        recommended_for=recommended_for,
        has_assets=body.get("has_assets") is True,
    )


def parse_presign_body(event: dict) -> PresignBody:
    files = util.parse_body(event).get("files")
    if not isinstance(files, list) or not all(
        isinstance(item, dict)
        and isinstance(item.get("kind"), str)
        and isinstance(item.get("content_type"), str)
        for item in files
    ):
        raise BadRequest("INVALID_FILES", "files requires kind and content_type")

    return PresignBody(
        files=[{"kind": f["kind"], "content_type": f["content_type"]} for f in files]
    )


def parse_finalize_body(event: dict) -> FinalizeBody:
    body = util.parse_body(event)
    result = FinalizeBody()

    if "gallery" in body:
        gallery = body["gallery"]
        if not isinstance(gallery, list) or not all(
            isinstance(item, dict)
            and (
                isinstance(item.get("key"), str) != isinstance(item.get("s3_key"), str)
            )
            for item in gallery
        ):
            raise BadRequest(
                "INVALID_FILES", "gallery items need exactly one of key or s3_key"
            )
        result["gallery"] = [
            {"key": item["key"]} if "key" in item else {"s3_key": item["s3_key"]}
            for item in gallery
        ]

    if "brochure" in body:
        brochure = body["brochure"]
        if brochure is not None and not (
            isinstance(brochure, dict) and isinstance(brochure.get("s3_key"), str)
        ):
            raise BadRequest("INVALID_FILES", "brochure must be null or {s3_key}")
        result["brochure"] = (
            None if brochure is None else {"s3_key": brochure["s3_key"]}
        )

    return result
