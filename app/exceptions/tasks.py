from .base import AppException
from fastapi_babel import _


class TaskNotFoundException(AppException):
    def __init__(self, task_id: int):
        super().__init__(
            status_code=404,
            message=_("Задача %(task_id)d не найдена.") % {"task_id": task_id},
            error_code="NOT_FOUND",
        )


class NotAuthorException(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            message=_("Доступ запрещен: действие разрешено только автору."),
            error_code="FORBIDDEN",
        )


class InvalidImportanceLevelException(AppException):
    def __init__(self):
        super().__init__(
            status_code=422,
            message=_(
                "Некорректная запись уровня важности.Возможные уровни: "
                "A - Важно и срочно, "
                "B - Важно и не срочно, "
                "C - Не важно и срочно, "
                "D - Не срочно и не важно."
            ),
            error_code="UNPROCESSABLE_ENTITY",
        )


class TaskAlreadyCompletedException(AppException):
    def __init__(self):
        super().__init__(
            status_code=400,
            message=_("Задача уже решена."),
            error_code="BAD_REQUEST",
        )
