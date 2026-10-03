import os

import pymysql
import pymysql.cursors
import requests

url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}


def get_sanity_docs():
    query = """
        *[
            _type == "courseTheme" 
        ] | order(_id) [0...100] {
            "sanityID": _id,
            title,
            "slug": value.current,
            "createdAt": _createdAt
        }
    """
    url = f"https://{os.environ['SANITY_PROJECT_ID']}.api.sanity.io/v{os.environ['SANITY_API_VERSION']}/data/query/{os.environ['SANITY_DATASET']}"
    headers = {"Authorization": f"Bearer {os.environ['SANITY_TOKEN']}"}

    r = requests.get(url, headers=headers, params={"query": query})
    r.raise_for_status()
    docs = r.json()["result"]

    return docs


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

    cursor.execute("SELECT id FROM course_theme")
    results = cursor.fetchall() or []
    for result in results:
        seen[result["id"]] = True

    for doc in get_sanity_docs():
        if doc["sanityID"] in seen:
            continue

        cursor.execute(
            """
                INSERT INTO course_theme(
                    id, sanity_id, title, slug, created_at, is_deleted
                ) VALUES (
                    %s, %s, %s, %s, %s, %s
                )
            """,
            (
                doc["sanityID"],
                doc["sanityID"],
                doc["title"],
                doc["slug"],
                doc["createdAt"],
                False,
            ),
        )
        connection.commit()

    connection.close()


def app():
    migrate()


app()

# a = [
#     {
#         "_createdAt": "2025-10-15T09:04:09Z",
#         "_id": "3e937005-323f-4e8c-8346-b71334f23bcb",
#         "_rev": "fkstx3XUD9b0PxPKNQnEsG",
#         "_system": {
#             "base": {
#                 "id": "3e937005-323f-4e8c-8346-b71334f23bcb",
#                 "rev": "fkstx3XUD9b0PxPKNQOLAp",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:22:53Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "well control",
#             "asset": {
#                 "_ref": "image-6dad124671733d196768f3126d34f01994463f4a-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "well control",
#             "asset": {
#                 "_ref": "image-cfd2f235edfb7ccb9d5035fdbe746e4b1eda4d37-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Well Control",
#         "value": {"_type": "slug", "current": "well-control"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:33:20Z",
#         "_id": "637d01dc-2128-45cc-b270-f06e8b192df2",
#         "_rev": "VNm5CakvghXMWI7oYrqsxL",
#         "_system": {
#             "base": {
#                 "id": "637d01dc-2128-45cc-b270-f06e8b192df2",
#                 "rev": "fkstx3XUD9b0PxPKNQeAV5",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:25:19Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "geothermal",
#             "asset": {
#                 "_ref": "image-fce42b2db40798ea9c5d128742e8c4fae91cb8fc-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "geothermal",
#             "asset": {
#                 "_ref": "image-b1a299779c8b58a2c6d143e5b478f4a58f308306-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Geothermal",
#         "value": {"_type": "slug", "current": "geothermal"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:33:05Z",
#         "_id": "91401b11-7e53-444a-87a7-88c8e3b27c56",
#         "_rev": "fkstx3XUD9b0PxPKNQoMgo",
#         "_system": {
#             "base": {
#                 "id": "91401b11-7e53-444a-87a7-88c8e3b27c56",
#                 "rev": "VNm5CakvghXMWI7oYrmciH",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:25:02Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "general safety",
#             "asset": {
#                 "_ref": "image-590e23b9d1a074266a3b948701af2579e43ec8b3-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "general safety",
#             "asset": {
#                 "_ref": "image-d3eb79926536e34626c3f752cee8a65762b07f96-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "General Safety",
#         "value": {"_type": "slug", "current": "general-safety"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:33:35Z",
#         "_id": "99dcf2f0-b5c8-4a10-ae9b-c61969535109",
#         "_rev": "pKSAzJc4Dek10AyKejptY1",
#         "_system": {
#             "base": {
#                 "id": "99dcf2f0-b5c8-4a10-ae9b-c61969535109",
#                 "rev": "VNm5CakvghXMWI7oYrnCja",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:25:44Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "mining",
#             "asset": {
#                 "_ref": "image-4dd494672632fa89faf34c027b61bcc3b3d0d540-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "mining",
#             "asset": {
#                 "_ref": "image-404f5aeabea21975467d7a4698a3f749102a67fc-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Mining",
#         "value": {"_type": "slug", "current": "mining"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:32:19Z",
#         "_id": "a179260a-7ea8-4fce-95e8-65e93481fe16",
#         "_rev": "fkstx3XUD9b0PxPKNQnWIV",
#         "_system": {
#             "base": {
#                 "id": "a179260a-7ea8-4fce-95e8-65e93481fe16",
#                 "rev": "VNm5CakvghXMWI7oYrlvKR",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:23:39Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "kemnaker",
#             "asset": {
#                 "_ref": "image-0823e50b743160066c714d2670b547d883633df2-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "kemnaker",
#             "asset": {
#                 "_ref": "image-4aaa25a6bfdc8d3e8353c488b99ddc6b06d8c430-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Kemnaker Training ",
#         "value": {"_type": "slug", "current": "kemnaker-training"},
#     },
#     {
#         "_createdAt": "2025-10-15T14:14:21Z",
#         "_id": "a403a1d5-b431-401c-8a37-75af4257df02",
#         "_rev": "VNm5CakvghXMWI7oYrqaRq",
#         "_system": {
#             "base": {
#                 "id": "a403a1d5-b431-401c-8a37-75af4257df02",
#                 "rev": "sWoWCWsXf3uCpny7e3bcxs",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:23:16Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "drilling industry",
#             "asset": {
#                 "_ref": "image-c78aa497317d685224da06c7dc2bc28ce044bca8-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "drilling industry",
#             "asset": {
#                 "_ref": "image-357b444c862ebe0d6255a11a5b3f3555072eef28-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Drilling Industry",
#         "value": {"_type": "slug", "current": "drilling-industry"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:32:35Z",
#         "_id": "a87a1618-3dc9-4571-ae1d-2317dc4985f7",
#         "_rev": "7X1BK9Xg2Xk2IKFHAIzb2I",
#         "_system": {
#             "base": {
#                 "id": "a87a1618-3dc9-4571-ae1d-2317dc4985f7",
#                 "rev": "VNm5CakvghXMWI7oYrqfxD",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2026-02-03T04:59:10Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "bnsp",
#             "asset": {
#                 "_ref": "image-cbb5d0e82716a39eab87469784e214b8cf5b13fe-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "bnsp",
#             "asset": {
#                 "_ref": "image-78761d88d3c36f12da2f06c4fb8f25bfc82b4f8e-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "BNSP & PPSDM Certification",
#         "value": {"_type": "slug", "current": "bnsp-and-ppsdm-certification"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:32:50Z",
#         "_id": "ba4e4b06-3018-427f-b812-2ee9285cad7e",
#         "_rev": "fkstx3XUD9b0PxPKNQoEre",
#         "_system": {
#             "base": {
#                 "id": "ba4e4b06-3018-427f-b812-2ee9285cad7e",
#                 "rev": "sWoWCWsXf3uCpny7e3cfL6",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:24:37Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "offshore",
#             "asset": {
#                 "_ref": "image-0c00be7c33b688a2bb8040a7961716fe96eb88fd-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "offshore",
#             "asset": {
#                 "_ref": "image-68173d2530611fc8e68aee18e79b488df99a5f23-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Offshore Safety",
#         "value": {"_type": "slug", "current": "offshore-safety"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:34:08Z",
#         "_id": "d4d3b8cf-46ef-4738-a0c2-65614a900720",
#         "_rev": "VNm5CakvghXMWI7oYrqzXt",
#         "_system": {
#             "base": {
#                 "id": "d4d3b8cf-46ef-4738-a0c2-65614a900720",
#                 "rev": "VNm5CakvghXMWI7oYrnfpm",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:27:02Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "technical",
#             "asset": {
#                 "_ref": "image-74545eb449be38e980a413cf71229542c26cb44e-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "technical",
#             "asset": {
#                 "_ref": "image-74013c0202f7e89cc9c29716f2e72916d221960e-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Technical Skill",
#         "value": {"_type": "slug", "current": "technical-skill"},
#     },
#     {
#         "_createdAt": "2025-11-07T16:33:51Z",
#         "_id": "f08b8c70-399a-4445-98d0-fef847dde545",
#         "_rev": "pKSAzJc4Dek10AyKejpy8k",
#         "_system": {
#             "base": {
#                 "id": "f08b8c70-399a-4445-98d0-fef847dde545",
#                 "rev": "VNm5CakvghXMWI7oYrnGyo",
#             }
#         },
#         "_type": "courseTheme",
#         "_updatedAt": "2025-11-18T07:26:16Z",
#         "icon": {
#             "_type": "mediaImg",
#             "alt": "softskill",
#             "asset": {
#                 "_ref": "image-0b5b9afcd0b0d2f21a1bde054a65797286a63132-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "iconHover": {
#             "_type": "mediaImg",
#             "alt": "softskill",
#             "asset": {
#                 "_ref": "image-e2ef79cbd4f284fb2b8dec4cde1dc2e6f97a0ca4-85x85-svg",
#                 "_type": "reference",
#             },
#         },
#         "title": "Softskill & Food Safety",
#         "value": {"_type": "slug", "current": "softskill-and-food-safety"},
#     },
# ]
