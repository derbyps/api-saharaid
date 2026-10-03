import os

import pymysql
import pymysql.cursors
import requests
from uuid_v7.base import uuid7

url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}


def get_sanity_docs():
    query = """
        array::unique(*[
        _type == "course"
        ].certificateValidity)
    """
    url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
    headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}

    r = requests.get(url, headers=headers, params={"query": query})
    r.raise_for_status()
    docs = r.json()["result"]

    return docs


def get_unique(values: list[str]) -> list[str]:

    seen = set()
    unique = []

    for value in values:
        key = value.lower()

        if key not in seen:
            seen.add(key)
            unique.append(value)

    return unique


def migrate():

    connection = pymysql.connect(
        host=os.environ["RDS_HOST"],
        user=os.environ["RDS_USER"],
        password=os.environ["RDS_PASSWORD"],
        database=os.environ["RDS_DATABASE"],
        cursorclass=pymysql.cursors.DictCursor,
    )
    cursor = connection.cursor()

    seen = {}

    cursor.execute("SELECT title FROM course_certificate_validity")
    results = cursor.fetchall() or []
    for result in results:
        seen[result["title"]] = True

    unique_docs = get_unique(get_sanity_docs())

    for doc in unique_docs:
        if doc in seen:
            continue

        cursor.execute(
            """
                INSERT INTO course_certificate_validity(
                    id, title, created_at, is_deleted
                ) VALUES (
                    %s, %s, %s, %s
                )
            """,
            (
                str(uuid7()),
                doc,
                pymysql.Timestamp.now(),
                False,
            ),
        )
        connection.commit()

    connection.close()


def app():
    migrate()


app()
