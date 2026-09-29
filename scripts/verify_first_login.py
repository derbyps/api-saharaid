"""Complete a Cognito first-login password challenge without calling the backend."""

import argparse
import getpass
import boto3
from botocore.exceptions import BotoCoreError, ClientError


def verify_challenge(auth: dict) -> None:
    if (
        auth.get("ChallengeName") != "NEW_PASSWORD_REQUIRED"
        or not isinstance(auth.get("Session"), str)
        or not auth["Session"]
        or "AuthenticationResult" in auth
    ):
        raise ValueError("Cognito did not return a new-password challenge without tokens")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("user_pool_id")
    parser.add_argument("app_client_id")
    parser.add_argument("email")
    args = parser.parse_args()

    password = getpass.getpass("Temporary password: ")
    try:
        cognito = boto3.client(
            "cognito-idp", region_name=args.user_pool_id.split("_", 1)[0]
        )
        auth = cognito.admin_initiate_auth(
            UserPoolId=args.user_pool_id,
            ClientId=args.app_client_id,
            AuthFlow="USER_AUTH",
            AuthParameters={
                "USERNAME": args.email,
                "PREFERRED_CHALLENGE": "PASSWORD",
                "PASSWORD": password,
            },
        )
        verify_challenge(auth)

        new_password = getpass.getpass("New password: ")
        if not new_password or new_password != getpass.getpass("Confirm new password: "):
            raise ValueError("new passwords must match and cannot be empty")

        result = cognito.admin_respond_to_auth_challenge(
            UserPoolId=args.user_pool_id,
            ClientId=args.app_client_id,
            ChallengeName="NEW_PASSWORD_REQUIRED",
            ChallengeResponses={"USERNAME": args.email, "NEW_PASSWORD": new_password},
            Session=auth["Session"],
        )
        if result.get("ChallengeName") or not result.get("AuthenticationResult", {}).get("AccessToken"):
            raise ValueError("Cognito did not complete authentication")
    except ClientError as error:
        code = error.response.get("Error", {}).get("Code", "unknown error")
        raise SystemExit(f"Cognito authentication failed ({code})") from error
    except BotoCoreError as error:
        raise SystemExit(f"Could not reach Cognito ({type(error).__name__})") from error
    except ValueError as error:
        raise SystemExit(str(error)) from error

    print("PASS: new password accepted; Cognito authentication completed.")


if __name__ == "__main__":
    main()
