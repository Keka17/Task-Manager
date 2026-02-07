from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db_connection
from app.db.models import User as UserModel
from app.api.schemas.users import UserCreate, User as UserSchema

from app.core.config import get_settings
from app.services.user_service import UserService
from app.dependencies.deps import admin_required, get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

settings = get_settings()

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM


@router.post(
    "/signup",
    response_model=UserSchema,
    summary="Registration of a new user in the system",
    description="**Creates a new account in the system**:  \n"
    "- Checks the **uniqueness** of the email address and phone number. \n\n"
    "- **Hashes** the password before saving.  \n"
    "- Throws an error if the data is already **taken**.",
)
async def signup(user: UserCreate, session: AsyncSession = Depends(get_db_connection)):
    """
    User registration endpoint with storage in the database.
    """
    new_user = await UserService.signup(user, session)
    return new_user


@router.get(
    "/",
    response_model=list[UserSchema],
    summary="List of all users",
    description="Retrieves a full list of all registered users from the database.  \n\n"
    "**Security**: a valid **Access Token** is required in the Authorisation header.",
    responses={
        401: {"description": "Unauthorized"},
    },
)
async def get_users(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Extracts all users from the database.
    Only available with a valid Access Token in the Authorization header.
    """
    return await UserService.get_users(session)


@router.get(
    "/{user_id}",
    response_model=UserSchema,
    summary="Retrieve a specific user by ID",
    description="Retrieves detailed information about the user.  \n\n"
    "**Security**: a valid **Access Token** is required in the Authorisation header.",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "User not found"},
    },
)
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_connection),
):
    """
    Returns a user by their id.
    Only available with a valid Access Token in the Authorization header.
    """
    return await UserService.get_user_by_id(user_id, session)


@router.delete(
    "/{user_id}",
    summary="Deleting a user",
    description="**Completely removes** the user and their tasks from the database.  \n"
    "Requires **admin** rights (verified via access token). \n"
    "**Warning**: This operation cannot be undone.  \n\n"
    "**Security**: a valid **Access Token** is required in the Authorisation header.",
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Admin's access is required."},
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
