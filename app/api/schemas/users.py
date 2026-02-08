from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
import re
from fastapi_babel import _
from app.core.config import get_settings

settings = get_settings()


# For documentation
def example_user_in(schema: dict) -> None:
    schema["example"] = {
        "name": "Michael Scott",
        "position": "World's best boss",
        "email": "dundermifflin@gmail.com",
        "phone": "89777907157",
        "password": "Str0ngP@$$w678",
    }


def example_user_out(schema: dict) -> None:
    schema["example"] = {
        "name": "Michael Scott",
        "position": "World's best boss",
        "email": "dundermifflin@gmail.com",
        "phone": "89777907157",
        "id": 94,
    }


def example_login(schema: dict) -> None:
    schema["example"] = {
        "email": "dundermifflin@gmail.com",
        "password": "Str0ngP@$$w678",
    }


class UserBase(BaseModel):
    name: str
    position: str
    email: EmailStr
    phone: str


class UserCreate(UserBase):
    password: str

    @field_validator("position")
    @classmethod
    def check_position(cls, position: str) -> str:
        positions = settings.POSITIONS
        if positions:
            positions_list = positions.split(",")
            allowed_positions = ", ".join(positions_list)
            error_msg = _("Позиции не существует. Доступные позиции:")
            full_msg = f"{error_msg}\n{allowed_positions}"
            if position not in positions_list:
                raise ValueError(full_msg)

        return position

    @field_validator("email")
    @classmethod
    def check_email(cls, email: str) -> EmailStr:
        # Define allowed corporate domain
        allowed_domain = settings.COMPANY_DOMAIN

        if allowed_domain:
            if not email.lower().endswith(f"@{allowed_domain}"):
                raise ValueError(
                    _(f"Регистрация доступна только для сотрудников: @{allowed_domain}")
                )

        return email.lower()

    @field_validator("password")
    @classmethod
    def check_password(cls, password: str) -> str:
        pattern = (
            r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{12,}$"
        )

        if re.fullmatch(pattern, password):
            return password
        else:
            raise ValueError(
                _(
                    "Слабый пароль! Рекомендации по созданию надежного пароля:"
                    "минимальная длина - 12 символов, буквы верхнего и нижнего регистра,"
                    "как минимум одна цифра и специальные символы (@$!%*?&)"
                )
            )

    @field_validator("phone")
    @classmethod
    def check_phone(cls, phone: str) -> str:
        pattern = r"^8\d{10}$"
        phone_ = phone.strip().replace(" ", "")

        if re.fullmatch(pattern, phone_):
            return phone
        else:
            raise ValueError(
                _(
                    "Некорректная запись! Номер телефона должен начинаться с 8 и состоять из 11 цифр."
                )
            )

    model_config = ConfigDict(json_schema_extra=example_user_in)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True, json_schema_extra=example_user_out)


class UserLogin(BaseModel):
    email: str
    password: str

    model_config = ConfigDict(json_schema_extra=example_login)
