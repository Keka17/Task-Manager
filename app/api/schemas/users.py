from pydantic import BaseModel, field_validator, EmailStr, ConfigDict, ValidationInfo
import re
from app.core.config import get_settings

settings = get_settings()


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
            if position not in positions_list:
                raise ValueError(
                    f"Позиции не существует. Доступные позиции:\n{allowed_positions}"
                )

        return position

    @field_validator("email")
    @classmethod
    def check_email(cls, email: str) -> EmailStr:
        # Define allowed corporate domain
        allowed_domain = settings.COMPANY_DOMAIN

        if allowed_domain:
            if not email.lower().endswith(f"@{allowed_domain}"):
                raise ValueError(
                    f"Регистрация доступна только для сотрудников: @{allowed_domain}"
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
                "Слабый пароль! Рекомендации по созданию надежного пароля:"
                "минимальная длина - 12 символов, буквы верхнего и нижнего регистра,"
                "как минимум одна цифра и специальные символы (@$!%*?&)"
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
                "Некорректная запись! Номер телефона должен начинаться с 8 и состоять из 11 цифр."
            )


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    email: str
    password: str
