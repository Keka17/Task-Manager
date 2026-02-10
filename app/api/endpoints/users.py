from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.db.models import User as UserModel
from app.api.schemas.users import UserCreate, User as UserSchema

from app.core.config import get_settings
from app.services.user_service import UserService
from app.dependencies.deps import admin_required, get_current_user_cookie

router = APIRouter(prefix="/users", tags=["Users"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


@router.post(
    "/signup",
    summary="Registering a new user and starting verification",
    description="Creates a new account with limited rights:  \n"
    "- Checks the **uniqueness** of the email address and phone number. \n\n"
    "- **Hashes** the password before saving.  \n"
    "- Creates a record in the database with status **'is_verified=False'**.  \n"
    "- **Backround Task**: Sends an email with a confirmation link.  \n\n"
    "- **Accept-Lanuage** options: ru (defult), en.  \n\n"
    "After registration, the user **must confirm** their email before login process. "
    "Otherwise, their profile **will be deleted**.",
    responses={400: {"description": "Bad Request"}, 409: {"description": "Conflict"}},
)
async def signup(
    user: UserCreate,
    backgroud_tasks: BackgroundTasks,
    accept_language: Optional[str] = Header("ru"),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    User registration endpoint with storage in the database.
    """
    return await UserService.signup(user, accept_language, session, backgroud_tasks)


@router.get(
    "/signup_confirm",
    summary="Registration confirmation via link",
    description="Activates a usser account: \n\n"
    "- Accepts a **temporary token** from the URL.  \n\n"
    "- Verifies the **digital signature** and the **token's lifetime** (10 minutes).  \n\n"
    "If verification is successful, sets **'is_verified=True'**.",
)
async def confirm_signup(
    request: Request,
    token: str,
    accept_language: Optional[str] = Header("ru"),
    session: AsyncSession = Depends(get_db_connection),
):
    return await UserService.confirm_email(request, token, accept_language, session)


@router.get(
    "/",
    response_model=list[UserSchema],
    summary="List of all users",
    description="Retrieves a full list of all registered users from the database.  \n\n"
    "**Security**: a valid **Access Token** is required in cookies 🍪.",
    responses={
        401: {"description": "Unauthorized"},
    },
)
async def get_users(
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Extracts all users from the database.
    Only available with a valid Access Token in cookies.
    """
    return await UserService.get_users(session)


@router.get(
    "/me",
    response_model=UserSchema,
    summary="User information",
    description="Retrieves user information from the database. \n\n"
    "**Security**: a valid **Access Token** is required in cookies 🍪.",
)
async def get_me(current_user: UserModel = Depends(get_current_user_cookie)):
    return current_user


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Retrieve a specific user by ID",
    description="Retrieves detailed information about the user.  \n\n"
    "**Security**: a valid **Access Token** is required in cookies 🍪.",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user_cookie),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Returns a user by their id.
    Only available with a valid Access Token in cookies.
    """
    return await UserService.get_user_by_id(user_id, session)


@router.delete(
    "/{user_id}",
    summary="Deleting a user",
    description="**Completely removes** the user and their tasks from the database.  \n\n"
    "Requires **admin** rights (field `is_superuser` in the database). \n\n"
    "**Warning**: This operation cannot be undone!",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Admin's access is required."},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    user_id: int,
    session: AsyncSession = Depends(get_db_connection),
    admin: UserModel = Depends(admin_required),
):
    """
    Deletes a user by their ID.
    Only available to users with administrative privileges.
    """
    return await UserService.delete_user_by_id(user_id, session)
