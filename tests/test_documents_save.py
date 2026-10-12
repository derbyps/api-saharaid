import unittest
from unittest.mock import patch

from functions.documents.services.document import DocumentService
from shared.exception import BadRequest

OWNER = {"type": "instructor", "id": "06acb55e-953f-732f-8000-d9300c031068"}


def _file(document_type, content_type):
    return {
        "document_type": document_type,
        "s3_key": f"docs/instructor/{OWNER['id']}/{document_type}",
        "content_type": content_type,
    }


class SaveDocumentsTest(unittest.TestCase):
    def _service(self):
        with patch.dict("os.environ", {"S3_BUCKET": "b"}), patch(
            "functions.documents.services.document.AWSManager.S3Manager"
        ):
            service = DocumentService()
        service._is_owner_valid = lambda owner: True
        return service

    def test_saves_content_type(self):
        service = self._service()
        files = [
            _file("passport_photo", "image/png"),
            _file("curiculum_vitae", "application/pdf"),
        ]
        with patch("functions.documents.services.document.db") as db, patch.object(
            service, "repo"
        ):
            service.save_documents(OWNER, files, [])
        saved = db.session.bulk_save_objects.call_args[0][0]
        self.assertEqual(
            [d.content_type for d in saved], ["image/png", "application/pdf"]
        )

    def test_rejects_missing_or_wrong_content_type(self):
        service = self._service()
        bad = [_file("curiculum_vitae", "image/png")]
        missing = [{k: v for k, v in bad[0].items() if k != "content_type"}]
        for files in (bad, missing):
            with self.assertRaises(BadRequest), patch.object(service, "repo"):
                service.save_documents(OWNER, files, [])


if __name__ == "__main__":
    unittest.main()
