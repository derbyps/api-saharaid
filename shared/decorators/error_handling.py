from functools import wraps

from sqlalchemy.exc import IntegrityError

from shared import util
from shared.configs.db import db


def handle_errors(handler):
    @wraps(handler)
    def wrapped(event, context):
        db.open()
        try:
            return handler(event, context)
        except util.HttpError as exc:
            return util.return_response(
                exc.status, {"error": str(exc), "errCode": exc.code}
            )
        except IntegrityError as exc:
            constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", "")
            if constraint in {
                "participants_active_name_key",
                "participants_active_phone_key",
            }:
                return util.return_response(
                    409,
                    {
                        "error": "Participant already exists",
                        "errCode": "PARTICIPANT_ALREADY_EXISTS",
                    },
                )

            return util.return_response(
                409, {"error": "Database constraint conflict", "errCode": "CONFLICT"}
            )
        except:
            return util.return_response(
                500, {"error": "Internal server error", "errCode": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    return wrapped
