from .base import AppException
from fastapi_babel import _


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404,
            message=_("Пользователь не найден."),
            error_code="NOT_FOUND",
        )


class EmailAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            status_code=409,
            message=_("Почта %(email)s занята.") % {"email": email},
            error_code="CONFLICT",
        )


class PhoneAlreadyExistsException(AppException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=409,
            message=_("Номер %(phone)s занят.") % {"phone": phone},
            error_code="CONFLICT",
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message=_("Неверные учетные данные."),
            error_code="INVALID_CREDENTIALS",
        )


class AdminAccessRequired(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message=_("Запрещено: требуется доступ администратора."),
            error_code="FORBIDDEN",
        )


class UnauthorizedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=401, message=_("Вы не авторизованы."), error_code="UNAUTHORIZED"
        )
