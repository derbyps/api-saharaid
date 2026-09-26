import json
import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch
from uuid import UUID, uuid4

from botocore.exceptions import ClientError
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from functions.documents.lambda_function import lambda_handler as documents_handler
from functions.participant.lambda_function import lambda_handler as participant_handler
from shared.configs.db import Base
from shared.models.document import Document, DocumentDeletion
from shared.models.participant import Participant
from shared.models.user import User


class ParticipantFlowTest(unittest.TestCase):
    def test_create_upload_read_download_and_remove_document(self):
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
                if isinstance(item, Document):
                    item.id = uuid4()
                    item.uploaded_at = datetime.now(timezone.utc)

        event.listen(Session, "before_flush", database_defaults)
        try:
            with sessions.begin() as session:
                session.add(User(id=actor_id, name="Admin", email="admin@example.com"))

            cognito = Mock()
            cognito.get_user.return_value = {"UserAttributes": [{"Name": "email", "Value": "admin@example.com"}]}
            s3 = Mock()
            s3.generate_presigned_url.return_value = "https://s3.example/upload"
            s3.head_object.return_value = {"ContentLength": 123, "ContentType": "image/png"}

            def request(path, body=None, method="POST", path_parameters=None):
                handler = documents_handler if path.startswith(("/files/", "/documents")) else participant_handler
                response = handler({
                    "rawPath": path,
                    "requestContext": {"http": {"method": method}, "authorizer": {"jwt": {"claims": {"token_use": "access"}}}},
                    "headers": {"authorization": "Bearer test-token"},
                    "pathParameters": path_parameters,
                    "body": json.dumps(body) if body is not None else None,
                }, None)
                return response["statusCode"], json.loads(response["body"])

            participant = {
                "name": " Alice ", "identity_number": "123", "gender": "female",
                "phone_number": " 08123 ", "email": "ALICE@example.com",
                "date_of_birth": "2000-01-02", "religion": "", "address": "",
                "job_position": "", "job_company": "", "education": "",
                "cr_number": "", "tax_number": "",
            }
            with patch("shared.configs.db._session_factory", return_value=sessions), \
                 patch("shared.util._cognito", return_value=cognito), \
                 patch("shared.AWSManager.boto3.client", return_value=s3), \
                 patch.dict("os.environ", {"S3_BUCKET": "test-bucket"}):
                status, created = request("/participant", participant)
                self.assertEqual(status, 201)
                self.assertEqual(created["participant"]["name"], "Alice")
                self.assertEqual(created["participant"]["serial_number"], 1)
                owner_id = created["participant"]["id"]
                status, detail = request(f"/participant/{owner_id}", method="GET", path_parameters={"id": owner_id})
                self.assertEqual((status, detail["documents"]), (200, []))
                self.assertEqual(detail["participant"], created["participant"])

                upload = {"owner": {"type": "participant", "id": owner_id}, "files": [{
                    "filename": "photo.png", "content_type": "image/png", "file_size": 123,
                    "document_type": "passport_photo",
                }]}
                status, signed = request("/files/presign-upload", upload)
                self.assertEqual(status, 200)
                self.assertEqual(signed["expires_in"], 900)
                key = signed["files"][0]["s3_key"]
                self.assertTrue(key.startswith(f"documents/participant/{owner_id}/"))
                s3.generate_presigned_url.assert_called_once_with(
                    "put_object",
                    Params={"Key": key, "ContentType": "image/png", "Bucket": "test-bucket"},
                    ExpiresIn=900, HttpMethod=None,
                )

                document = {"owner": upload["owner"], "documents": [{
                    "document_type": "passport_photo", "s3_key": key,
                    "original_filename": "photo.png", "content_type": "image/png",
                    "file_size": 123, "last_modified_at": "2026-09-25T12:00:00+07:00",
                }]}
                status, bad = request("/documents", {**document, "documents": [{**document["documents"][0], "s3_key": "other/key"}]})
                self.assertEqual((status, bad["errCode"]), (400, "INVALID_DOCUMENT"))
                s3.head_object.return_value = {"ContentLength": 124, "ContentType": "image/png"}
                status, bad = request("/documents", document)
                self.assertEqual((status, bad["errCode"]), (400, "UPLOAD_MISMATCH"))
                s3.head_object.return_value = {"ContentLength": 123, "ContentType": "image/png"}
                s3.head_object.reset_mock()
                status, saved = request("/documents", document)
                self.assertEqual(status, 200)
                self.assertEqual(len(saved["documents"]), 1)
                self.assertNotIn("s3_key", saved["documents"][0])
                s3.head_object.assert_called_once_with(Bucket="test-bucket", Key=key)

                status, detail = request(f"/participant/{owner_id}", method="GET", path_parameters={"id": owner_id})
                self.assertEqual(status, 200)
                self.assertEqual(detail["documents"], saved["documents"])

                doc_id = saved["documents"][0]["id"]
                s3.generate_presigned_url.return_value = "https://s3.example/download"
                status, download = request("/files/presign-download", {"owner_type": "participant", "document_id": doc_id})
                self.assertEqual((status, download["expires_in"]), (200, 3600))
                self.assertEqual(download["download_url"], "https://s3.example/download")
                s3.generate_presigned_url.assert_called_with(
                    "get_object", Params={"Key": key, "Bucket": "test-bucket"},
                    ExpiresIn=3600, HttpMethod=None,
                )

                status, bad = request("/documents", document)
                self.assertEqual((status, bad["errCode"]), (409, "DOCUMENT_ALREADY_EXISTS"))

                removal = {"owner": upload["owner"], "documents": [], "remove_ids": [doc_id]}
                s3.delete_object.side_effect = ClientError({"Error": {"Code": "ServiceUnavailable"}}, "DeleteObject")
                status, failed = request("/documents", removal)
                self.assertEqual((status, failed["errCode"]), (502, "S3_CLEANUP_PENDING"))
                with sessions() as session:
                    self.assertIsNone(session.get(Document, UUID(doc_id)))
                    self.assertIsNotNone(session.get(DocumentDeletion, UUID(doc_id)))

                s3.delete_object.side_effect = None
                status, removed = request("/documents", removal)
                self.assertEqual((status, removed["documents"]), (200, []))
                self.assertEqual(s3.delete_object.call_count, 2)
                s3.delete_object.assert_called_with(Bucket="test-bucket", Key=key)
                with sessions() as session:
                    self.assertIsNone(session.get(DocumentDeletion, UUID(doc_id)))
                status, missing = request("/files/presign-download", {"owner_type": "participant", "document_id": doc_id})
                self.assertEqual((status, missing["errCode"]), (404, "DOCUMENT_NOT_FOUND"))
        finally:
            event.remove(Session, "before_flush", database_defaults)
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
