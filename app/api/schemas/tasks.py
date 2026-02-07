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
from fastapi_babel import _

from app.core.config import get_settings

settings = get_settings()


# For documentation
def example_task_in(schema: dict) -> None:
    schema["example"] = {
        "title": "The 'Dundies' Awards Ceremony",
        "content": "Write personal (but not offensive!) nominations for each colleague.",
        "importance_level": "C",
    }


def example_task_update(schema: dict) -> None:
    schema["example"] = {
        "content": "Use quirks and funny moments, avoid sensitive topics."
    }


def example_remark_create(schema: dict) -> None:
    schema["example"] = {"remark": "Michael's forced fun with a musical climax."}


def example_task_out(schema: dict) -> None:
    schema["example"] = {
        "title": "The 'Dundies' Awards Ceremony",
        "content": "Write personal (but not offensive!) nominations for each colleague",
        "importance_level": "C",
        "id": 12,
        "user_email": "dundermifflin@gmail.com",
        "remark": "Michael's forced fun with a musical climax.",
        "created_at": "2026-01-29 14:59",
        "deadline_date": "2026-01-31 19:00",
        "updated_at": "2026-01-30 02:12",
        "completed_at": "Null",
    }


class TaskBase(BaseModel):
    title: str
    content: str
    importance_level: Annotated[str, StringConstraints(min_length=1, max_length=1)]


class TaskCreate(TaskBase):
    @field_validator("title")
    @classmethod
    def check_title(cls, title: str) -> str:
        if title[0].isalpha() and not title[0].isupper():
            raise ValueError(_("Заголовок должен начинаться с заглавной буквы!"))
        return title

    @field_validator("content")
    @classmethod
    def check_content(cls, content: str) -> str:
        if content[0].isalpha() and not content[0].isupper():
            raise ValueError(
                _("Содержание задачи должно начинаться с заглавной буквы!")
            )
        return content

    @field_validator("importance_level")
    @classmethod
    def check_level(cls, level: str) -> str:
        levels = ["A", "B", "C", "D"]
        if level not in levels:
            raise ValueError(
                _(
                    "Некорректная запись уровня важности."
                    "\nВозможные уровни:"
                    "\n🔴 A - Важно и срочно"
                    "\n🟢 B - Важно и не срочно"
                    "\n🟡 C - Не важно и срочно"
                    "\n🟣 D - Не срочно и не важно"
                )
            )
        return level

    model_config = ConfigDict(json_schema_extra=example_task_in)


class TaskUpdate(BaseModel):
    content: Optional[str] = None

    model_config = ConfigDict(json_schema_extra=example_task_update)


class TaskUpdateAdmin(BaseModel):
    remark: Optional[str] = None

    model_config = ConfigDict(json_schema_extra=example_remark_create)


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

    model_config = ConfigDict(from_attributes=True, json_schema_extra=example_task_out)
