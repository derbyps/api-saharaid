import json
import unittest
from unittest.mock import ANY, Mock, patch
from uuid import uuid4

from functions.documents.lambda_function import lambda_handler


class DocumentsPresignTest(unittest.TestCase):
    def test_file_fields_and_upload(self):
        owner_id = str(uuid4())
        file = {"filename": "IMG-20260814-WA0036.jpg", "content_type": "image/jpeg"}
        owner = {"type": "participant", "id": owner_id}

        def request(files, owner_type: object = "participant"):
            response = lambda_handler(
                {
                    "rawPath": "/files/presign-upload",
                    "requestContext": {"http": {"method": "POST"}},
                    "body": json.dumps(
                        {"owner": {**owner, "type": owner_type}, "files": files}
                    ),
                },
                None,
            )
            return response["statusCode"], json.loads(response["body"])

        repository = Mock()
        repository.get_active_owner.return_value = True
        repository.list_for_owner.return_value = []
        repository.pending_for_owner.return_value = []
        repository.save.return_value = []
        s3_manager = Mock()
        s3_manager.generate_presigned_url.return_value = "https://s3.example/upload"
        s3_manager.head_object.return_value = {
            "ContentLength": 123,
            "ContentType": "image/jpeg",
        }

        with (
            patch(
                "functions.documents.services.document.DocumentRepository",
                return_value=repository,
            ),
            patch(
                "functions.documents.services.document.AWSManager.S3Manager",
                return_value=s3_manager,
            ),
            patch("functions.documents.handlers.POST.util.current_user_id"),
            patch("shared.decorators.error_handling.db.open"),
            patch("shared.decorators.error_handling.db.close"),
            patch.dict("os.environ", {"S3_BUCKET": "test-bucket"}),
        ):
            status, error = request([file], ["instructor"])
            self.assertEqual((status, error["errCode"]), (400, "INVALID_OWNER"))

            status, error = request(
                [{**file, "file_size": 123, "document_type": "passport_photo"}],
                "../certificate",
            )
            self.assertEqual((status, error["errCode"]), (400, "INVALID_OWNER"))

            status, error = request([file])
            self.assertEqual((status, error["errCode"]), (400, "INVALID_FILES"))
            self.assertIn("file_size", error["error"])
            repository.get_active_owner.assert_not_called()

            status, signed = request(
                [{**file, "file_size": 123, "document_type": "passport_photo"}]
            )
            self.assertEqual(status, 200)
            self.assertEqual(signed["expires_in"], 900)
            self.assertEqual(len(signed["files"]), 1)
            self.assertEqual(
                signed["files"][0]["s3_key"],
                f"docs/participant/{owner_id}/passport_photo",
            )
            repository.get_active_owner.assert_not_called()

            status, signed = request(
                [
                    {
                        "filename": "cv.pdf",
                        "content_type": "application/pdf",
                        "file_size": 123,
                        "document_type": "curiculum_vitae",
                    }
                ],
                "instructor",
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                signed["files"][0]["s3_key"],
                f"docs/instructor/{owner_id}/curiculum_vitae",
            )

            status, signed = request(
                [
                    {
                        "filename": "certificate.pdf",
                        "content_type": "application/pdf",
                        "file_size": 123,
                        "document_type": "completion_certificate",
                    }
                ],
                "certificate",
            )
            self.assertEqual(status, 200)
            self.assertEqual(
                signed["files"][0]["s3_key"],
                f"docs/certificate/{owner_id}/completion_certificate",
            )

            response = lambda_handler(
                {
                    "rawPath": "/documents",
                    "requestContext": {"http": {"method": "POST"}},
                    "body": json.dumps(
                        {
                            "owner": owner,
                            "documents": [
                                {
                                    "document_type": "passport_photo",
                                    "s3_key": f"docs/participant/{owner_id}/passport_photo",
                                    "original_filename": file["filename"],
                                    "content_type": "image/jpeg",
                                    "file_size": 123,
                                    "last_modified_at": "2026-09-25T12:00:00+07:00",
                                }
                            ],
                        }
                    ),
                },
                None,
            )
            self.assertEqual(response["statusCode"], 200)
            repository.get_active_owner.assert_called_with(ANY)
            s3_manager.head_object.assert_called_once_with(
                Key=f"docs/participant/{owner_id}/passport_photo"
            )


if __name__ == "__main__":
    unittest.main()
