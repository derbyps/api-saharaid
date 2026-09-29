import ssl
import unittest
from unittest.mock import patch

from shared.configs.db import _session_factory


class DatabaseConfigTest(unittest.TestCase):
    def test_rds_connection_uses_tls_and_separate_credentials(self):
        environment = {
            "RDS_HOST": "database.example.com",
            "RDS_USER": "app_user",
            "RDS_PASSWORD": "password@with/slash",
            "RDS_DATABASE": "app_db",
        }

        _session_factory.cache_clear()
        with patch.dict("os.environ", environment), patch("shared.configs.db.create_engine") as create_engine:
            _session_factory()

        url = create_engine.call_args.args[0]
        self.assertEqual((url.host, url.username, url.password, url.database), (
            "database.example.com", "app_user", "password@with/slash", "app_db",
        ))
        self.assertEqual(url.drivername, "mysql+pymysql")
        self.assertEqual(url.query["charset"], "utf8mb4")
        connect_args = create_engine.call_args.kwargs["connect_args"]
        self.assertEqual(connect_args["init_command"], "SET time_zone = '+07:00'")
        self.assertTrue(connect_args["ssl"].check_hostname)
        self.assertEqual(connect_args["ssl"].verify_mode, ssl.CERT_REQUIRED)
        _session_factory.cache_clear()


if __name__ == "__main__":
    unittest.main()
