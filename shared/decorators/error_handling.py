from functools import wraps

from shared import util
from shared.configs.db import db
from shared.schemas.response import ErrorResponse
from shared.exception import (
    AppException,
    BadRequest,
    Conflict,
    Forbidden,
    Gone,
    InternalServerError,
    MethodNotImplemented,
    NotAcceptable,
    NotFound,
    TooLarge,
    Unauthorized,
    UnprocessableEntity,
)


def _error_response(status: int, code: str, message: str) -> dict:
    response: ErrorResponse = {"error": message, "errCode": code}
    return util.return_response(status, response)


def handle_errors(handler):
    @wraps(handler)
    def wrapped(event, context):
        db.open()
        try:
            return handler(event, context)
        except util.HttpError as exc:
            return _error_response(exc.status, exc.code, str(exc))

        except BadRequest as exc:
            return _error_response(400, exc.code, str(exc))

        except Unauthorized as exc:
            return _error_response(401, exc.code, str(exc))

        except Forbidden as exc:
            return _error_response(403, exc.code, str(exc))

        except NotFound as exc:
            return _error_response(404, exc.code, str(exc))

        except MethodNotImplemented as exc:
            return _error_response(405, exc.code, str(exc))

        except NotAcceptable as exc:
            return _error_response(406, exc.code, str(exc))

        except Conflict as exc:
            return _error_response(409, exc.code, str(exc))

        except Gone as exc:
            return _error_response(410, exc.code, str(exc))

        except TooLarge as exc:
            return _error_response(413, exc.code, str(exc))

        except UnprocessableEntity as exc:
            return _error_response(422, exc.code, str(exc))

        except InternalServerError as exc:
            return _error_response(500, exc.code, str(exc))

        except AppException as exc:
            return _error_response(500, exc.code, str(exc))

        except:
            return _error_response(500, "INTERNAL_ERROR", "Internal server error")
        finally:
            db.close()

    return wrapped
