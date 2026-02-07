from datetime import timedelta
from typing import Optional

import strawberry
from graphql import GraphQLError
from pydantic import ValidationError

from src.core.user.exceptions import (
    UserNotFoundError,
    UserCreationError,
    TokenCreationError,
)
from src.core.user.entities import CreateUser
from src.core.user.services import (
    UserService,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    TokenData,
)
from src.api.graphql.schemas import UserSchema, UserInput, TokenSchema


@strawberry.type
class Query:

    @strawberry.field(description="Get User query.")
    def user(self, id: int) -> UserSchema:
        user = UserService.get_by_id(id)
        if not user:
            raise UserNotFoundError()
        return UserSchema(
            id=id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            permissions=user.permissions,
        )

    @strawberry.field(description="Get all Users query.")
    def all_users(self) -> list[UserSchema]:
        users = [
            UserSchema(
                id=user[0],
                username=user[1].username,
                email=user[1].email,
                is_admin=user[1].is_admin,
                permissions=user[1].permissions,
            )
            for user in UserService.get_all()
        ]
        return users


@strawberry.type
class Mutation:

    @strawberry.mutation(description="Create new user.")
    def register(
        self, user: UserInput, permissions: Optional[list[str]] = None
    ) -> UserSchema:
        if permissions is None:
            permissions = []

        try:
            data = CreateUser(
                username=user.username,
                email=user.email,
                password=user.password,
                is_admin=user.is_admin,
                permissions=permissions,
            )
        except ValidationError as e:
            raise GraphQLError(str(e))

        created_user = UserService.add(data, permissions)
        return UserSchema(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_admin=created_user.is_admin,
            permissions=created_user.permissions,
        )

    @strawberry.mutation(description="User Login.")
    def login(self, username: str, password: str) -> TokenSchema:
        user = UserService.authenticate_user(username, password)
        if user is None:
            raise UserCreationError("Incorrect username or password")
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
            raise GraphQLError(str(e))

        return TokenSchema(access_token=access_token, refresh_token=refresh_token)
