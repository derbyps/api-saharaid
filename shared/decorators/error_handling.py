from functools import wraps

from shared import util
from shared.configs.db import db
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

        except BadRequest as exc:
            return util.return_response(400, {"error": str(exc), "errCode": exc.code})

        except Unauthorized as exc:
            return util.return_response(401, {"error": str(exc), "errCode": exc.code})

        except Forbidden as exc:
            return util.return_response(403, {"error": str(exc), "errCode": exc.code})

        except NotFound as exc:
            return util.return_response(404, {"error": str(exc), "errCode": exc.code})

        except MethodNotImplemented as exc:
            return util.return_response(405, {"error": str(exc), "errCode": exc.code})

        except NotAcceptable as exc:
            return util.return_response(406, {"error": str(exc), "errCode": exc.code})

        except Conflict as exc:
            return util.return_response(409, {"error": str(exc), "errCode": exc.code})

        except Gone as exc:
            return util.return_response(410, {"error": str(exc), "errCode": exc.code})

        except TooLarge as exc:
            return util.return_response(413, {"error": str(exc), "errCode": exc.code})

        except UnprocessableEntity as exc:
            return util.return_response(422, {"error": str(exc), "errCode": exc.code})

        except InternalServerError as exc:
            return util.return_response(500, {"error": str(exc), "errCode": exc.code})

        except AppException as exc:
            return util.return_response(500, {"error": str(exc), "errCode": exc.code})

        except:
            return util.return_response(
                500, {"error": "Internal server error", "errCode": "INTERNAL_ERROR"}
            )
        finally:
            db.close()

    return wrapped
