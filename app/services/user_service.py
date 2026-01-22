import bcrypt
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User as UserModel
from app.exceptions.users import (
    UserNotFoundException,
    EmailAlreadyExistsException,
    PhoneAlreadyExistsException,
    AdminAccessRequired,
)


class UserService:
    @staticmethod
    async def signup(user, session: AsyncSession):
        """
        User registration function with storage in the database.
        """
        query = select(UserModel).where(
            or_(UserModel.email == user.email, UserModel.phone == user.phone)
        )
        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
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

        return new_user
