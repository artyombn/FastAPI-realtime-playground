from typing import Optional

from fastapi import APIRouter, Query

from users.managers import user_manager
from users.schema import (
    UserListOutput,
    UserOutput,
    UserBase,
    AdminUser,
    RegularUser,
    PERMISSIONS,
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
    result = UserListOutput(
        total_users=len(user_manager.get_all_users()),
        users=user_manager.get_all_users(),
    )
    return result


@user_router.get(
    "/{user_id}",
    response_model=UserOutput,
    summary="Get a user",
    description="Returns a user with the given ID.",
)
async def get_user_by_user_id(user_id: int) -> UserOutput:
    user = user_manager.get_user_by_user_id(user_id)
    user_output = UserOutput(
        id=user.id,
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
    user: UserBase,
    permissions: Optional[list[str]] = Query(
        default=None,
        title="Permissions",
        example=PERMISSIONS,
        enum=PERMISSIONS,
    ),
) -> UserOutput:
    if user.is_admin:
        result = AdminUser(
            username=user.username,
            email=user.email,
        )
    else:
        result = RegularUser(
            username=user.username,
            email=user.email,
            permissions=permissions,
        )
    updated_user = user_manager.add_user(result)
    return updated_user
