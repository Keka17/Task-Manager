import bcrypt
from sqlalchemy import select, delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User as UserModel
from app.exceptions.users import (
    EmailAlreadyExistsException,
    PhoneAlreadyExistsException,
    UserNotFoundException,
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

    @staticmethod
    async def get_users(session: AsyncSession):
        query = select(UserModel)
        result = await session.execute(query)

        return result.scalars().all()

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int):
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        return user_in_db

    @staticmethod
    async def delete_user_by_id(session: AsyncSession, user_id: int) -> dict:
        """
        Deletes a user by their ID.
        This endpoint is allowed to users with administrative privileges (by access token) only.
        """
        query = select(UserModel).where(UserModel.id == user_id)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        query = delete(user_in_db)
        await session.execute(query)
        await session.commit()

        return {"message": f"User with id {user_id} was successfully deleted."}
