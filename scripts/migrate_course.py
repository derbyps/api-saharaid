import os

import pymysql
import pymysql.cursors
import requests
from uuid_v7.base import uuid7

url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}


def get_sanity_course():
    query = """
        *[
            _type == "course"
        ] | order(_id) [0...1000] {
            "sanityID": _id,
            "name": title,
            "certificate_validity": certificateValidity,
            "slug": slug.current,
            "course_modes": courseMode,
            "course_themes": themes[]._ref,
            "created_at": _createdAt
        }
    """
    url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
    headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}

    r = requests.get(url, headers=headers, params={"query": query})
    r.raise_for_status()
    docs = r.json()["result"]

    return docs


def map_course_mode(course_modes: list) -> str | None:
    # course mode contains ['online', 'offline'] only
    # guarantee at least one course mode and element is online and offline

    if len(course_modes) == 2:
        return "0199D8A1-9A63-7D53-B2E9-4CA6F70815D9"  # Offline/Online

    if course_modes[0] == "online":
        return "0199D8A1-7C42-7B31-9E6F-2A84C5D103B7"

    if course_modes[0] == "offline":
        return "0199D8A1-8F56-7C42-A1D8-3B95E6F204C8"

    return None


def sync_course_themes(cursor, course_id: str, theme_ids: list[str] | None) -> None:
    unique_theme_ids = list(dict.fromkeys(theme_ids or []))

    cursor.execute("DELETE FROM course_theme_detail WHERE course_id = %s", (course_id,))

    if unique_theme_ids:
        cursor.executemany(
            "INSERT INTO course_theme_detail (id, course_id, course_theme_id) VALUES (%s, %s, %s)",
            [(str(uuid7()), course_id, theme_id) for theme_id in unique_theme_ids],
        )


def update_course(cursor, validities, doc):
    course_class_type_id = map_course_mode(doc["course_modes"])
    course_certificate_validity_id = validities[doc["certificate_validity"].lower()]

    cursor.execute(
        """
        UPDATE course
        SET
            name = %s,
            slug = %s,
            course_certificate_validity_id = %s,
            course_class_type_id = %s,
            updated_at = %s
        WHERE id = %s
    """,
        (
            doc["name"],
            doc["slug"],
            course_certificate_validity_id,
            course_class_type_id,
            doc["created_at"],
            doc["sanityID"],
        ),
    )


def insert_course(cursor, validities, doc):

    course_class_type_id = map_course_mode(doc["course_modes"])
    course_certificate_validity_id = validities[doc["certificate_validity"].lower()]

    cursor.execute(
        """
            INSERT INTO course(
                id, sanity_id, name, slug, course_certificate_validity_id, course_class_type_id, created_at, is_deleted
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s
            )
        """,
        (
            doc["sanityID"],
            doc["sanityID"],
            doc["name"],
            doc["slug"],
            course_certificate_validity_id,
            course_class_type_id,
            doc["created_at"],
            False,
        ),
    )


def migrate():

    connection = pymysql.connect(
        host=os.environ["RDS_HOST"],
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        database=os.environ["RDS_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()

    cursor.execute("SELECT id FROM course")
    results = cursor.fetchall() or []

    seen = {}
    validities = {}

    for result in results:
        seen[result["id"]] = True

    cursor.execute("select id, title as name from course_certificate_validity")
    db_ceritificate_validities = cursor.fetchall() or []
    for db_ceritificate_validity in db_ceritificate_validities:
        validities[db_ceritificate_validity["name"].lower()] = db_ceritificate_validity[
            "id"
        ]

    sanity_courses = get_sanity_course()

    for idx, doc in enumerate(sanity_courses):
        print(f"{idx + 1}/{len(sanity_courses)}")

        if doc["sanityID"] in seen:
            update_course(cursor, validities, doc)

        else:
            insert_course(cursor, validities, doc)

        sync_course_themes(cursor, doc["sanityID"], doc["course_themes"])

    connection.commit()
    connection.close()


migrate()
