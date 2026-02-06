from .base import AppException
from fastapi_babel import _


class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message=_("Время жизни токена истекло."),
            error_code="TOKEN_EXPIRED",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message=_("Невалидный токен."), error_code="INVALID_TOKEN"
        )


class InvalidTokenTypeException(AppException):
    def __init__(self, expected_type: str):
        super().__init__(
            status_code=401,
            message=_("Невалидный тип токена. Ожидается: %(expected_type)s.")
            % {"expected_type": expected_type},
            error_code="INVALID_TOKEN_TYPE",
        )


class TokenRevokedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message=_("Токен аннулирован."),
            error_code="TOKEN_REVOKED",
        )
