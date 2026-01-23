from .base import AppException


class TaskNotFoundException(AppException):
    def __init__(self, task_id):
        super().__init__(
            status_code=404,
            message=f"Задача {task_id} не найдена.",
            error_code="NOT FOUND",
        )


class NotAuthorException(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message="Доступ запрещен: действие разрешено только автору.",
            error_code="FORBIDDEN",
        )
