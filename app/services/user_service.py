import bcrypt
from itsdangerous import URLSafeTimedSerializer, BadSignature
from sqlalchemy import select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_babel import _
from fastapi import BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from app.api.schemas.users import UserCreate
from app.db.models import User as UserModel
from app.exceptions.users import (
    EmailAlreadyExistsException,
    PhoneAlreadyExistsException,
    UserNotFoundException,
)
from app.utils.send_email import send_confirmation_email
from app.core.config import get_settings
from pathlib import Path

TEMPLATE_FOLDER = Path(__file__).parent.parent / "templates"

settings = get_settings()
SECRET_KEY = settings.SECRET_KEY
frontend_url = settings.FRONTEND_URL

templates = Jinja2Templates(directory=TEMPLATE_FOLDER)

s = URLSafeTimedSerializer(settings.SECRET_KEY)


class UserService:
    @staticmethod
    async def signup(
        user: UserCreate,
        accept_language: str,
        session: AsyncSession,
        background_tasks: BackgroundTasks,
    ):
        query = select(UserModel).where(
            or_(UserModel.email == user.email, UserModel.phone == user.phone)
        )
        result = await session.execute(query)
        existing_users = result.scalars().all()

        print(f"DEBUG {existing_users}")

        if existing_users:
            for existing_user in existing_users:
                if existing_user.email == user.email:
                    raise EmailAlreadyExistsException(email=user.email)
                if existing_user.phone == user.phone:
                    raise PhoneAlreadyExistsException(phone=user.phone)

        password_bytes = bytes(user.password, "utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

        new_user = UserModel(
            name=user.name,
            hashed_password=hashed.decode("utf-8"),
            position=user.position,
            email=user.email,
            phone=user.phone,
        )

        session.add(new_user)
        await session.commit()

        await session.refresh(new_user)

        s = URLSafeTimedSerializer(settings.SECRET_KEY)
        confirmation_token = s.dumps(
            new_user.email
        )  # Secure token to confirm registration
        confirmation_url = (
            f"{settings.FRONTEND_URL}/users/signup_confirm?token={confirmation_token}"
        )

        accept_language = accept_language.split(",")[0].split("-")[0]

        if accept_language == "en":
            background_tasks.add_task(
                send_confirmation_email,
                new_user.email,
                confirmation_url,
                "Email confirmation",
                "en/email_confirmation.html",
            )
        else:
            background_tasks.add_task(
                send_confirmation_email,
                new_user.email,
                confirmation_url,
                "Подтверждение электронной почты",
                "ru/email_confirmation.html",
            )

        print(f"🟢 DEBUG: confirmation link: {confirmation_url}")

        return {
            "message": _(
                f"Для завершения регистрации необходимо подтвердить email. "
                "Пожалуйста, проверьте вашу почту. Если профиль не будет подтвержден "
                f"в течение 10 минут, он будет автоматически удален."
            )
        }

    @staticmethod
    async def confirm_email(
        request: Request, token: str, accept_lanuage: str, session: AsyncSession
    ) -> HTMLResponse:
        accept_language = accept_lanuage.split(",")[0].split("-")[0]
        try:
            email = s.loads(
                token, max_age=600
            )  # The token is valid for 60 * 10 (10 mins)
        except BadSignature:
            template_name = (
                "en/invalid_link.html"
                if accept_language == "en"
                else "ru/invalid_link.html"
            )
            return templates.TemplateResponse(request=request, name=template_name)

        query = (
            update(UserModel).where(UserModel.email == email).values(is_verified=True)
        )
        await session.execute(query)
        await session.commit()

        template_name = (
            "en/email_confirmed.html"
            if accept_lanuage == "en"
            else "ru/email_confirmed.html"
        )

        return templates.TemplateResponse(request=request, name=template_name)

    @staticmethod
    async def get_users(session: AsyncSession):
        query = select(UserModel)
        result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(user_id: int, session: AsyncSession):
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        return user_in_db

    @staticmethod
    async def delete_user_by_id(user_id: int, session: AsyncSession) -> dict:
        """
        Deletes a user by their ID.
        This endpoint is allowed to users with administrative privileges (by access token) only.
        """
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        await session.delete(user_in_db)
        await session.commit()

        return {
            "message": _("Пользователь с id = %(user_id)d успешно удален.")
            % {"user_id": user_id}
        }
