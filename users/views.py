from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Query, HTTPException, Depends
from starlette import status
from starlette.status import HTTP_400_BAD_REQUEST

from users.managers import (
    user_manager,
    UserAlreadyExistsError,
    UserNotFoundError,
    UserCreationError,
)
from users.schema import (
    UserListOutput,
    UserOutput,
    CreateUser,
    PERMISSIONS,
    UserOutputWithHashedPWD,
)
from users.services import (
    UserService,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    TokenData,
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)

user_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@user_router.get(
    "/",
    response_model=UserListOutput,
    summary="Get list of users",
    description="Returns a list of all users with the total number of them.",
)
async def get_users() -> UserListOutput:
    users = UserService.get_all()
    output_users = [
        UserOutput(
            id=user[0],
            username=user[1].username,
            email=user[1].email,
            is_admin=user[1].is_admin,
            permissions=user[1].permissions,
        )
        for user in users
    ]
    result = UserListOutput(
        total_users=len(users),
        users=output_users,
    )
    return result


@user_router.get(
    "/{user_id}",
    response_model=UserOutput,
    summary="Get a user",
    description="Returns a user with the given ID.",
)
async def get_user_by_user_id(user_id: int) -> UserOutput:
    try:
        user = UserService.get_by_id(user_id)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    user_output = UserOutput(
        id=user_id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        permissions=user.permissions,
    )
    return user_output


@user_router.post(
    "/create",
    response_model=UserOutput,
    summary="Create a new user",
    description="Creates a new user and returns the created user with an assigned ID.",
)
async def create_user(
    user: CreateUser,
    permissions: Optional[list[str]] = Query(
        default=None,
        title="Permissions",
        example=PERMISSIONS,
        enum=PERMISSIONS,
    ),
) -> UserOutput:
    try:
        created_user = UserService.add(user, permissions)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except UserCreationError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))

    return created_user


@user_router.get(
    "login",
    response_model=UserOutputWithHashedPWD,
    summary="User Login",
    description="Login user using access token and refresh token",
)
async def login(username: str, password: str) -> dict:
    user = UserService.authenticate_user(username, password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)

    data_access_token = TokenData(
        sub=username,
        is_admin=user.is_admin,
        extra={
            "user_id": user.id,
            "type": "access_token",
            "access_token_expires": int(access_token_expires.total_seconds()),
        },
    )
    data_refresh_token = TokenData(
        sub=username,
        is_admin=user.is_admin,
        extra={
            "user_id": user.id,
            "type": "refresh_token",
            "refresh_token_expires": int(refresh_token_expires.total_seconds()),
        },
    )
    try:
        access_token = UserService.create_token(
            data=data_access_token, expires_delta=access_token_expires
        )
        refresh_token = UserService.create_token(
            data=data_refresh_token, expires_delta=refresh_token_expires
        )
    except TokenCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


@user_router.post(
    "/refresh",
    response_model=str,
    summary="Refresh user",
    description="Refresh user using access token and refresh token",
)
async def refresh_user(token: str) -> str:
    try:
        username = UserService.verify_token(token, "refresh_token")
    except TokenExpiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TokenIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except TokenTypeIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    user_tuple = user_manager.get_by_username(username)
    if not user_tuple:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Wrong username or password during token refresh",
        )

    user_id = user_tuple[0]
    user = user_tuple[1]

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    new_access_token = TokenData(
        sub=user.username,
        is_admin=user.is_admin,
        extra={
            "user_id": user_id,
            "type": "access_token",
            "access_token_expires": int(access_token_expires.total_seconds()),
        },
    )

    try:
        access_token = UserService.create_token(
            data=new_access_token, expires_delta=access_token_expires
        )
    except TokenCreationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    return f"Access Token was refreshed: {access_token}"


@user_router.put(
    "/me",
    response_model=UserOutput,
    summary="Get my info",
    description="Get info about myself with hashed password",
)
async def me(current_user=Depends(UserService.get_current_user_from_jwt)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return current_user
