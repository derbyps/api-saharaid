import unittest
from unittest.mock import patch

from scripts.verify_first_login import main, verify_challenge


class VerifyFirstLoginTest(unittest.TestCase):
    def test_calls_cognito_directly_without_printing_secrets(self):
        with patch("sys.argv", ["verify_first_login", "ap-southeast-1_pool", "client", "admin@example.com"]), \
             patch("scripts.verify_first_login.getpass.getpass", side_effect=["temporary-password", "new-password", "new-password"]), \
             patch("scripts.verify_first_login.boto3.client") as client_factory, \
             patch("builtins.print") as print_output:
            client_factory.return_value.admin_initiate_auth.return_value = {
                "ChallengeName": "NEW_PASSWORD_REQUIRED", "Session": "opaque-session"
            }
            client_factory.return_value.admin_respond_to_auth_challenge.return_value = {
                "AuthenticationResult": {"AccessToken": "access-token"}
            }
            main()

        client_factory.assert_called_once_with("cognito-idp", region_name="ap-southeast-1")
        client_factory.return_value.admin_initiate_auth.assert_called_once_with(
            UserPoolId="ap-southeast-1_pool",
            ClientId="client",
            AuthFlow="USER_AUTH",
            AuthParameters={
                "USERNAME": "admin@example.com",
                "PREFERRED_CHALLENGE": "PASSWORD",
                "PASSWORD": "temporary-password",
            },
        )
        client_factory.return_value.admin_respond_to_auth_challenge.assert_called_once_with(
            UserPoolId="ap-southeast-1_pool",
            ClientId="client",
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={"USERNAME": "admin@example.com", "NEW_PASSWORD": "new-password"},
            Session="opaque-session",
        )
        self.assertNotIn("opaque-session", str(print_output.call_args))
        self.assertNotIn("temporary-password", str(print_output.call_args))
        self.assertNotIn("new-password", str(print_output.call_args))
        self.assertNotIn("access-token", str(print_output.call_args))

    def test_accepts_only_challenge_without_tokens(self):
        challenge = {"ChallengeName": "NEW_PASSWORD_REQUIRED", "Session": "opaque"}
        verify_challenge(challenge)

        for body in (
            {**challenge, "Session": ""},
            {**challenge, "AuthenticationResult": {"AccessToken": "access"}},
            {**challenge, "ChallengeName": "OTHER_CHALLENGE"},
        ):
            with self.assertRaises(ValueError):
                verify_challenge(body)


if __name__ == "__main__":
    unittest.main()
