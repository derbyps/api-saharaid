class AppException(Exception):
    """Base exception with a message and optional metadata."""

    def __init__(self, code: str, message: str | None = None):
        self.message = message or ""
        self.code = code


class BadRequest(AppException):
    pass


class Unauthorized(AppException):
    pass


class Forbidden(AppException):
    pass


class NotFound(AppException):
    pass


class MethodNotImplemented(AppException):
    pass


class NotAcceptable(AppException):
    pass


class Conflict(AppException):
    pass


class Gone(AppException):
    pass


class UnprocessableEntity(AppException):
    pass


class TooLarge(AppException):
    pass


class UnavailableForLegalReasons(AppException):
    pass


class InternalServerError(AppException):
    pass
