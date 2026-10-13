import json
import unittest
from unittest.mock import patch

from functions.enrollment.lambda_function import lambda_handler
from functions.enrollment.services.enrollment import EnrollmentService
from shared.configs.db import db
from shared.exception import Conflict, NotFound

BODY = {"schedule_id": "s1", "participant_ids": ["p1", "p2"]}


class EnrollmentServiceTest(unittest.TestCase):
    def _service(self, **repo):
        service = EnrollmentService()
        defaults = {
            "schedule_exists": True,
            "get_active_participant_ids": {"p1", "p2"},
            "get_enrolled_participant_ids": set(),
        }
        for name, value in {**defaults, **repo}.items():
            setattr(service.repo, name, lambda *_, value=value: value)
        return service

    def test_creates_one_row_per_participant(self):
        service = self._service()
        with patch("functions.enrollment.services.enrollment.db") as fake_db:
            result = service.create(BODY, "actor")
        self.assertEqual(result, {"inserted": 2})
        saved = [call.args[0] for call in fake_db.save.call_args_list]
        self.assertEqual([row.participant_id for row in saved], ["p1", "p2"])
        self.assertEqual({row.schedule_id for row in saved}, {"s1"})
        self.assertEqual({row.created_by for row in saved}, {"actor"})
        fake_db.commit.assert_called_once()

    def test_rejects_the_whole_request_without_saving(self):
        cases = [
            (NotFound, {"schedule_exists": False}),
            (NotFound, {"get_active_participant_ids": {"p1"}}),
            (Conflict, {"get_enrolled_participant_ids": {"p2"}}),
        ]
        for error, repo in cases:
            with self.subTest(repo=repo), patch(
                "functions.enrollment.services.enrollment.db"
            ) as fake_db:
                with self.assertRaises(error):
                    self._service(**repo).create(BODY, "actor")
                fake_db.save.assert_not_called()
                fake_db.commit.assert_not_called()


class EnrollmentRouteTest(unittest.TestCase):
    def _post(self, body):
        event = {
            "requestContext": {"http": {"method": "POST"}},
            "rawPath": "/enrollment",
            "body": json.dumps(body),
        }
        with (
            patch.object(db, "open"),
            patch.object(db, "close"),
            patch(
                "functions.enrollment.handlers.POST.util.current_user_id",
                return_value="actor",
            ),
            patch("functions.enrollment.handlers.POST.EnrollmentService") as service,
        ):
            service.return_value.create.return_value = {"inserted": 1}
            response = lambda_handler(event, None)
        return response["statusCode"], json.loads(response["body"]), service

    def test_valid_request_returns_201_with_inserted_count(self):
        status, body, service = self._post(
            {"schedule_id": "s1", "participant_ids": ["p1", "p1"]}
        )
        self.assertEqual((status, body), (201, {"inserted": 1}))
        # Duplicate ids in the request are collapsed before the service sees them.
        self.assertEqual(
            service.return_value.create.call_args.args[0],
            {"schedule_id": "s1", "participant_ids": ["p1"]},
        )

    def test_invalid_bodies_return_400(self):
        for body in (
            {},
            {"schedule_id": "s1"},
            {"schedule_id": "s1", "participant_ids": []},
            {"schedule_id": "s1", "participant_ids": [1]},
            {"schedule_id": "", "participant_ids": ["p1"]},
        ):
            with self.subTest(body=body):
                self.assertEqual(self._post(body)[0], 400)


if __name__ == "__main__":
    unittest.main()
