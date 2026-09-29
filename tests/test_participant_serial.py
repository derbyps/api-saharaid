import json
import unittest
from unittest.mock import Mock, patch
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from functions.participant.lambda_function import lambda_handler
from shared.configs.db import Base
from shared.models.document import DocumentDeletion
from shared.models.participant import Participant
from shared.models.user import User


class ParticipantSerialTest(unittest.TestCase):
    def test_create_uses_max_serial_including_deleted_participants(self):
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        sessions = sessionmaker(engine, expire_on_commit=False)
        with sessions.begin() as session:
            session.add(User(id=str(uuid4()), name="Admin", email="admin@example.com"))

        cognito = Mock()
        cognito.get_user.return_value = {
            "UserAttributes": [{"Name": "email", "Value": "admin@example.com"}]
        }
        participant = {
            "name": "Alice", "identity_number": "123", "gender": "female",
            "phone_number": "08123", "email": "alice@example.com",
            "date_of_birth": "2000-01-02", "religion": "", "address": "",
            "job_position": "", "job_company": "", "education": "",
            "cr_number": "", "tax_number": "",
        }

        def create(name):
            response = lambda_handler({
                "requestContext": {
                    "http": {"method": "POST"},
                    "authorizer": {"jwt": {"claims": {"token_use": "access"}}},
                },
                "headers": {"authorization": "Bearer test-token"},
                "body": json.dumps({**participant, "name": name}),
            }, None)
            self.assertEqual(response["statusCode"], 201)
            return json.loads(response["body"])["participant"]

        with patch("shared.configs.db._session_factory", return_value=sessions), \
             patch("shared.util._cognito", return_value=cognito):
            first = create("Alice")
            self.assertEqual(first["serial_number"], 1)
            with sessions.begin() as session:
                saved = session.get(Participant, first["id"])
                assert saved is not None
                saved.is_deleted = True
            second = create("Bob")
            self.assertEqual(second["serial_number"], 2)

        self.assertEqual(
            [column.name for column in DocumentDeletion.__mapper__.primary_key],
            ["document_id"],
        )
        engine.dispose()


if __name__ == "__main__":
    unittest.main()
