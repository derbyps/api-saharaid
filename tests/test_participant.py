import json
import unittest
from datetime import datetime, timezone
from unittest.mock import patch
from uuid import UUID, uuid4

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from functions.participant.lambda_function import lambda_handler
from shared.configs.db import Base
from shared.models.document import Document
from shared.models.participant import Participant
from shared.models.user import User


class ParticipantFlowTest(unittest.TestCase):
    def test_create_list_detail_edit(self):
        engine = create_engine("sqlite:///:memory:")
        event.listen(engine, "connect", lambda connection, _: connection.execute("ATTACH DATABASE ':memory:' AS public"))
        Base.metadata.create_all(engine)
        sessions = sessionmaker(engine, expire_on_commit=False)
        actor_id = uuid4()

        def database_defaults(session, *_):
            for item in session.new:
                if isinstance(item, Participant):
                    item.id = uuid4()
                    item.serial_number = 1
                    item.created_at = datetime.now(timezone.utc)

        event.listen(Session, "before_flush", database_defaults)
        try:
            with sessions.begin() as session:
                session.add(User(id=actor_id, name="Admin", email="admin@example.com"))

            class Cognito:
                def get_user(self, **_):
                    return {"UserAttributes": [{"Name": "email", "Value": "admin@example.com"}]}

            def request(method, body=None, query=None):
                response = lambda_handler({
                    "requestContext": {"http": {"method": method}, "authorizer": {"jwt": {"claims": {"token_use": "access"}}}},
                    "headers": {"authorization": "Bearer test-token"},
                    "queryStringParameters": query,
                    "body": json.dumps(body) if body is not None else None,
                }, None)
                return response["statusCode"], json.loads(response["body"])

            payload = {
                "name": " Alice ", "identity_number": "123", "gender": "female",
                "phone_number": " 08123 ", "email": "alice@example.com",
                "date_of_birth": "2000-01-02", "religion": "", "address": "",
                "job_position": "", "job_company": "", "education": "",
                "cr_number": "", "tax_number": "",
            }
            with patch("shared.configs.db._session_factory", return_value=sessions), patch("shared.util._cognito", return_value=Cognito()):
                status, created = request("POST", payload)
                self.assertEqual(status, 201)
                self.assertEqual(created["participant"]["name"], "Alice")
                participant_id = created["participant"]["id"]
                with sessions.begin() as session:
                    session.add(Document(
                        id=uuid4(), participant_id=UUID(participant_id), document_type="passport_photo",
                        s3_key="participants/test/photo", original_filename="photo.png",
                        content_type="image/png", file_size=123,
                        last_modified_at=datetime.now(timezone.utc),
                        uploaded_at=datetime.now(timezone.utc), created_by=actor_id,
                    ))

                status, listed = request("GET", query={"p": "1", "rp": "12"})
                self.assertEqual((status, listed["pagination"]["total"]), (200, 1))
                self.assertEqual(len(listed["data"]), 1)
                self.assertNotIn("identity_number", listed["data"][0])
                self.assertEqual(request("GET", query={"created": "today", "sort": "name_asc"})[1]["pagination"]["total"], 1)
                self.assertEqual(request("GET", query={"created": "yesterday"})[1]["pagination"]["total"], 0)

                status, detail = request("GET", query={"id": participant_id})
                self.assertEqual(status, 200)
                self.assertEqual(detail["documents"][0]["document_type"], "passport_photo")
                self.assertNotIn("s3_key", detail["documents"][0])
                self.assertEqual(detail["participant"]["serial_number"], 1)

                status, edited = request("PUT", {**payload, "name": "Alice Updated"}, {"id": participant_id})
                self.assertEqual((status, edited["participant"]["name"]), (200, "Alice Updated"))
                self.assertEqual(request("GET", query={"created": "bad"})[0], 400)
                self.assertEqual(request("POST", {"name": "incomplete"})[0], 400)
        finally:
            event.remove(Session, "before_flush", database_defaults)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
