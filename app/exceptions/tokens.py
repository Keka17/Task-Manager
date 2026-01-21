from .base import AppException


class TokenExpiredException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Время жизни токена истекло.",
            error_code="TOKEN_EXPIRED",
        )


class InvalidTokenException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message="Невалидный токен.", error_code="INVALID_TOKEN"
        )


class InvalidTokenTypeException(AppException):
    def __init__(self, expected_type: str):
        super().__init__(
            status_code=401,
            message=f"Невалидный тип токена. Ожидается: {expected_type}.",
            error_code="INVALID_TOKEN_TYPE",
        )


class TokenRevokedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401,
            message="Токен аннулирован.",
            error_code="TOKEN_REVOKED",
        )
