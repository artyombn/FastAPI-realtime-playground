import logging
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from users.core.services import UserService
from users.api.rest.decorators import handle_user_errors
from users.dependencies import get_current_user_from_jwt, require_admin, get_session

from users.core.permissions import Permissions
from users.core.entities import (
    UserListResponse,
    UserResponse,
    CreateUser,
    UserLogin,
)
from users.core.services import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    TokenData,
)

logger = logging.getLogger("fastapi-app")

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.get(
    "/",
    response_model=UserListResponse,
    summary="Get list of users",
    description="Returns a list of all users with the total number of them.",
)
async def get_users(
    session: AsyncSession = Depends(db_helper.get_session),
    current_user=Depends(require_admin),
) -> UserListResponse:
    users = await UserService.get_all(session)
    result = UserListResponse(
        total_users=len(users),
        users=users,
    )
    return result


@user_router.get(
    "/me",
    response_model=UserResponse,
    summary="Get my info",
    description="Get info about myself with hashed password",
)
async def me(current_user=Depends(get_current_user_from_jwt)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Error: You didn't authenticate",
        )
    return current_user


@user_router.post(
    "/register",
    response_model=UserResponse,
    summary="Register a new user",
    description="Creates a new user and returns the created user with an assigned ID.",
)
@handle_user_errors
async def register_user(
    user: CreateUser,
    permissions: Optional[list[str]] = Query(
        default=[],
        title="Permissions",
        example=Permissions.list(),
        enum=Permissions.list(),
    ),
    session: AsyncSession = Depends(db_helper.get_session),
) -> UserResponse:
    created_user = await UserService.create(user, permissions, session)
    logger.info(
        f"User successfully created. id={created_user.id}, username={created_user.username}, email={created_user.email}"
    )
    return created_user


@user_router.post(
    "/login",
    response_model=dict,
    summary="User Login",
    description="Login user using access token and refresh token",
)
@handle_user_errors
async def login(
    user_login: UserLogin, session: AsyncSession = Depends(db_helper.get_session)
) -> dict:
    user = await UserService.authenticate_user(
        username=user_login.username, password=user_login.password, session=session
    )
    if user is None:
        logger.error(f"User authorization error. Username: {user_login.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    logger.info(f"User successfully authorized. Username: {user_login.username}")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    data_access_token = TokenData(
        sub=user.username,
        is_admin=user.is_admin,
        extra={
            "user_id": user.id,
            "type": "access_token",
            "access_token_expires": int(access_token_expires.total_seconds()),
        },
    )
    data_refresh_token = TokenData(
        sub=user.username,
        is_admin=user.is_admin,
        extra={
            "user_id": user.id,
            "type": "refresh_token",
            "refresh_token_expires": int(refresh_token_expires.total_seconds()),
        },
    )
    access_token = UserService.create_token(
        data=data_access_token, expires_delta=access_token_expires
    )
    refresh_token = UserService.create_token(
        data=data_refresh_token, expires_delta=refresh_token_expires
    )

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


@user_router.post(
    "/refresh",
    response_model=str,
    summary="Refresh user",
    description="Refresh user using access token and refresh token",
)
@handle_user_errors
async def refresh_user(
    token: str, session: AsyncSession = Depends(db_helper.get_session)
) -> str:
    username = UserService.verify_token(token, "refresh_token")

    user = await UserService.get_by_username(username, session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password during token refresh",
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    new_access_token = TokenData(
        sub=user.username,
        is_admin=user.is_admin,
        extra={
            "user_id": user.id,
            "type": "access_token",
            "access_token_expires": int(access_token_expires.total_seconds()),
        },
    )

    access_token = UserService.create_token(
        data=new_access_token, expires_delta=access_token_expires
    )

    return f"Access Token was refreshed: {access_token}"


@user_router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get a user",
    description="Returns a user with the given ID.",
)
@handle_user_errors
async def get_user_by_user_id(
    user_id: int,
    current_user=Depends(require_admin),
    session: AsyncSession = Depends(db_helper.get_session),
) -> UserResponse:
    user = await UserService.get_by_id(user_id, session)
    return user
