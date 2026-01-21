from .base import AppException


class UserNotFoundException(AppException):
    def __init__(self):
        super().__init__(
            status_code=404, message="Пользователь не найден.", error_code="NOT FOUND"
        )


class EmailAlreadyExistsException(AppException):
    def __init__(self, email: str):
        super().__init__(
            status_code=409, message=f"Почта {email} занята.", error_code="CONFLICT"
        )


class PhoneAlreadyExistsException(AppException):
    def __init__(self, phone: str):
        super().__init__(
            status_code=409, message=f"Номер {phone} занят.", error_code="CONFLICT"
        )


class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message="Неверные учетные данные.",
            error_code="UNAUTHORIZED",
        )


class AdminAccessRequired(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message="Запрещено: требуется доступ администратора.",
            error_code="FORBIDDEN",
        )
