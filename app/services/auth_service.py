import bcrypt
import datetime
import jwt
from jwt import PyJWTError

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RevokedToken, User as UserModel
from app.exceptions.users import UserNotFoundException, InvalidCredentialsException
from app.exceptions.tokens import (
    InvalidTokenException,
    InvalidTokenTypeException,
    TokenRevokedException,
)

from app.core.security import create_access_token, create_refresh_token
from app.core.config import get_settings

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


class AuthService:
    """
    Working with the creation/updating/decoding of tokens.
    """

    @staticmethod
    async def login(user_in, session: AsyncSession):
        """
        Verifying credentials to get a JWT token.
        """
        query = select(UserModel).where(UserModel.email == user_in.email)
        result = await session.execute(query)
        user_in_db = result.scalars().first()

        if not user_in_db:
            raise UserNotFoundException()

        if not bcrypt.checkpw(
            user_in.password.encode("utf-8"), user_in_db.hashed_password.encode("utf-8")
        ):
            raise InvalidCredentialsException()

        access_token = create_access_token({"sub": user_in.email})
        refresh_token = create_refresh_token({"sub": user_in.email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "sub": user_in.email,
        }

    @staticmethod
    async def refresh(x_refresh_token, session: AsyncSession):
        """
        Updates a pair of tokens.
        Accepts the old Refresh Token in Headers, revokes it (add to the database)
        and generates new Access and Refresh tokens.
        """
        try:
            payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        except PyJWTError:
            raise InvalidTokenException()

        if payload.get("token_type") != "refresh":
            raise InvalidTokenTypeException(expected_type="refresh")

        # Check the unique token ID in the revoked token database
        jti = payload.get("jti")

        query = select(RevokedToken).where(RevokedToken.jti == jti)
        result = await session.execute(query)
        is_revoked = result.scalars().first()

        if is_revoked:
            raise TokenRevokedException()

        # Revoke the current refresh token and add it to the database
        expire_timestamp = payload.get("exp")
        revoked_entry = RevokedToken(
            jti=jti,
            expires_at=datetime.datetime.fromtimestamp(
                expire_timestamp, tz=datetime.UTC
            ),
        )

        session.add(revoked_entry)

        email = payload.get("sub")
        new_access = create_access_token({"sub": email})
        new_refresh = create_refresh_token({"sub": email})

        await session.commit()

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer",
        }

    @staticmethod
    async def logout(x_refresh_token, session: AsyncSession):
        """
        Ends the user session. Accepts Refresh Token in Headers
        Retrieves the JTI from the current token and adds it to the database.
        """
        try:
            payload = jwt.decode(x_refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

            jti = payload.get("jti")
            exp = payload.get("exp")

            session.add(
                RevokedToken(
                    jti=jti,
                    expires_at=datetime.datetime.fromtimestamp(exp, tz=datetime.UTC),
                )
            )
            await session.commit()
        except:
            raise InvalidTokenException()

        return {"message": "Logged out successfully"}
