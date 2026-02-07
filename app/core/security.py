import jwt
import uuid
import datetime
from datetime import timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.exceptions.tokens import TokenExpiredException, InvalidTokenException
from app.exceptions.users import UnauthorizedException
from app.core.config import get_settings

settings = get_settings()

# Extracts the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS


def create_jwt_token(
    data: dict, expires_delta: timedelta, token_type: str, include_jti: bool = False
) -> str:
    """
    Function for creating a JWT token. It copies the input data,
    adds the expiration time, and encodes the token.
    """
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + expires_delta
    payload = {"exp": expire, "token_type": token_type, **to_encode}

    # JTI for refresh tokens
    if include_jti:
        payload["jti"] = str(uuid.uuid4())

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    if isinstance(token, bytes):
        return token.decode("utf-8")
    return token


def create_access_token(data: dict) -> str:
    """Creates access-type JWT token"""
    return create_jwt_token(
        data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), token_type="access"
    )


def create_refresh_token(data: dict) -> str:
    """Creates refresh-type JWT token"""
    return create_jwt_token(
        data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh", include_jti=True
    )


def decode_jwt_token(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Extracts user information from the access token.
    """
    if not token:
        raise UnauthorizedException()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.exceptions.InvalidTokenError as e:
        print(f"JWT Error: {e}")
        raise InvalidTokenException()


def decode_jwt_token_cookie(token: str) -> dict:
    """
    Extracts user information from the access token.
    """
    if not token:
        raise UnauthorizedException()
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.exceptions.ExpiredSignatureError:
        raise TokenExpiredException()
    except jwt.exceptions.InvalidTokenError as e:
        print(f"JWT Error: {e}")
        raise InvalidTokenException()
