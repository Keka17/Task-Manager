from pydantic import BaseModel, field_validator, EmailStr, ConfigDict
import re


class UserBase(BaseModel):
    name: str
    position: str
    email: EmailStr
    phone: str


class UserCreate(UserBase):
    password: str

    @field_validator("name")
    def check_name(cls, name) -> str:
        pattern = r"^[А-ЯЁ][а-яё]{1,30}(?:[- ][А-ЯЁ][а-яё]{1,30}){2}$"

        if re.fullmatch(pattern, name):
            return name
        else:
            raise ValueError("Некорректная запись ФИО!")

    @field_validator("position")
    def check_position(cls, position) -> str:
        positions_list = [
            "CEO",
            "Продакт-мененджер",
            "Frontend-разработчик",
            "Backend-разработчик",
            "UX-специалист",
            "SMM-специалист",
        ]
        allowed_positions = ", ".join(positions_list)

        if position not in positions_list:
            raise ValueError(
                f"Позиции не существует. Доступные позиции:\n{allowed_positions}"
            )

        return position

    @field_validator("password")
    def check_password(cls, password) -> str:
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
    def check_phone(cls, phone) -> str:
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
