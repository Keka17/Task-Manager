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


class InvalidImportanceLevelException(AppException):
    def __init__(self):
        super().__init__(
            status_code=422,
            message="Некорректная запись уровня важности.Возможные уровни: "
            "A - Важно и срочно, "
            "B - Важно и не срочно, "
            "C - Не важно и срочно, "
            "D - Не срочно и не важно.",
            error_code="UNPROCESSABLE ENTITY",
        )


class TaskAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message="Задача уже решена.",
            error_code="BAD REQUEST",
        )
