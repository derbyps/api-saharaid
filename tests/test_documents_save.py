import unittest
from types import SimpleNamespace
from unittest.mock import patch

from functions.documents.services.document import DocumentService
from shared.exception import BadRequest

OWNER = {"type": "instructor", "id": "06acb55e-953f-732f-8000-d9300c031068"}


def _file(document_type, content_type, original_filename="My File.pdf"):
    return {
        "document_type": document_type,
        "s3_key": f"docs/instructor/{OWNER['id']}/{document_type}",
        "content_type": content_type,
        "original_filename": original_filename,
    }


class SaveDocumentsTest(unittest.TestCase):
    def _service(self):
        with patch.dict("os.environ", {"S3_BUCKET": "b"}), patch(
            "functions.documents.services.document.AWSManager.S3Manager"
        ):
            service = DocumentService()
        service._is_owner_valid = lambda owner: True
        return service

    def test_saves_content_type_and_original_filename(self):
        service = self._service()
        files = [
            _file("passport_photo", "image/png", "Budi passport.png"),
            _file("curiculum_vitae", "application/pdf", "CV Budi.pdf"),
        ]
        with patch("functions.documents.services.document.db") as db, patch.object(
            service, "repo"
        ) as repo:
            repo.get_active_by_types.return_value = []
            service.save_documents(OWNER, files, [], "actor")
        saved = db.session.bulk_save_objects.call_args[0][0]
        self.assertEqual(
            [d.content_type for d in saved], ["image/png", "application/pdf"]
        )
        self.assertEqual(
            [d.original_filename for d in saved], ["Budi passport.png", "CV Budi.pdf"]
        )

    def test_replacement_updates_the_existing_row(self):
        service = self._service()
        existing = SimpleNamespace(
            id="doc-1",
            document_type="curiculum_vitae",
            s3_key="old",
            content_type="application/pdf",
            original_filename="old.pdf",
            updated_at=None,
            updated_by=None,
        )
        files = [_file("curiculum_vitae", "application/pdf", "new cv.pdf")]
        with patch("functions.documents.services.document.db") as db, patch.object(
            service, "repo"
        ) as repo:
            repo.get_active_by_types.return_value = [existing]
            service.save_documents(OWNER, files, ["doc-1", "doc-2"], "actor")
        # The replaced row is kept; only the unrelated removal id is deleted.
        repo.remove.assert_called_once_with(OWNER["id"], OWNER["type"], ["doc-2"])
        db.session.bulk_save_objects.assert_not_called()
        self.assertEqual(existing.original_filename, "new cv.pdf")
        self.assertIsNotNone(existing.updated_at)
        self.assertEqual(existing.updated_by, "actor")
        self.assertEqual(
            existing.s3_key, f"docs/instructor/{OWNER['id']}/curiculum_vitae"
        )

    def test_filename_is_kept_but_path_parts_are_dropped(self):
        clean = DocumentService._clean_filename
        self.assertEqual(clean("C:\\scans\\Ktp Budi (1).pdf"), "Ktp Budi (1).pdf")
        self.assertEqual(clean("../../etc/passwd\n"), "passwd")
        for bad in ("", "   ", None, 5):
            with self.assertRaises(BadRequest):
                clean(bad)

    def test_rejects_bad_files(self):
        service = self._service()
        wrong_type = [_file("curiculum_vitae", "image/png")]
        no_name = [
            {k: v for k, v in _file("curiculum_vitae", "application/pdf").items()
             if k != "original_filename"}
        ]
        no_content_type = [
            {k: v for k, v in wrong_type[0].items() if k != "content_type"}
        ]
        foreign_key = [
            {**_file("curiculum_vitae", "application/pdf"), "s3_key": "docs/x/y/z"}
        ]
        duplicate = [
            _file("curiculum_vitae", "application/pdf"),
            _file("curiculum_vitae", "application/pdf"),
        ]
        for files in (wrong_type, no_name, no_content_type, foreign_key, duplicate):
            with self.assertRaises(BadRequest), patch.object(service, "repo"):
                service.save_documents(OWNER, files, [], "actor")


if __name__ == "__main__":
    unittest.main()
