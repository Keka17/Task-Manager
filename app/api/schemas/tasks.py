from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    field_validator,
    PlainSerializer,
)
from datetime import datetime
from typing import Optional, Annotated
from zoneinfo import ZoneInfo

from app.core.config import get_settings

settings = get_settings()


class TaskBase(BaseModel):
    title: str
    content: str
    importance_level: Annotated[str, StringConstraints(min_length=1, max_length=1)]


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def check_title(cls, title: str) -> str:
        if not title[0].isupper():
            raise ValueError("Заголовок должен начинаться с заглавной буквы!")
        return title

    @field_validator("content")
    @classmethod
    def check_content(cls, content: str) -> str:
        if not content[0].isupper():
            raise ValueError("Содержание задачи должно начинаться с заглавной буквы!")
        return content

    @field_validator("importance_level")
    @classmethod
    def check_level(cls, level: str) -> str:
        levels = ["A", "B", "C", "D"]
        if level not in levels:
            raise ValueError(
                "Некорректная запись уровня важности."
                "\nВозможные уровни:"
                "\n🔴 A - Важно и срочно"
                "\n🟢 B - Важно и не срочно"
                "\n🟡 C - Не важно и срочно"
                "\n🟣 D - Не срочно и не важно"
            )
        return level


class TaskUpdate(BaseModel):
    content: Optional[str] = None


class TaskUpdateAdmin(BaseModel):
    remark: Optional[str] = None


# Custom datetime object output based on the time zone
LOCAL_TZ = ZoneInfo(settings.TZ_IANA)

DateTimeHuman = Annotated[
    datetime,
    PlainSerializer(
        lambda dt: dt.astimezone(LOCAL_TZ).strftime("%Y-%m-%d %H:%M"), return_type=str
    ),
]


class Task(TaskBase):
    id: int
    user_email: str
    remark: str | None = None
    created_at: DateTimeHuman
    deadline_date: DateTimeHuman | None = None
    updated_at: DateTimeHuman
    completed_at: DateTimeHuman | None = None

    model_config = ConfigDict(from_attributes=True)
