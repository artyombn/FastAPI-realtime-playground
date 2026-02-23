from datetime import timedelta
from typing import Optional

import strawberry
from graphql import GraphQLError
from pydantic import ValidationError
from strawberry.file_uploads import Upload

from src.config.paths import MEDIA_USERS_DIR
from src.api.graphql.decorators import paginate
from src.api.graphql.decorators import require_authentication
from src.core.exceptions import (
    UserNotFoundError,
    UserCreationError,
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from src.core.entities import CreateUser
from src.core.services import (
    UserService,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
    TokenData,
)
from src.api.graphql.user.schemas import UserSchema, UserInput, TokenSchema, UserPage


@strawberry.type
class UserQuery:

    @strawberry.field(description="Get User")
    async def user(self, id: int, info: strawberry.Info) -> UserSchema:
        session = info.context["session"]

        user = await UserService.get_by_id(id, session)
        if not user:
            raise UserNotFoundError()
        return UserSchema(
            id=id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            permissions=user.permissions,
        )

    @strawberry.field(description="Get all Users")
    @require_authentication
    @paginate(entity="user")
    async def all_users(
        self, info: strawberry.Info, limit: int, offset: int
    ) -> list[UserPage]:
        session = info.context["session"]

        users = [
            UserSchema(
                id=user[0],
                username=user[1].username,
                email=user[1].email,
                is_admin=user[1].is_admin,
                permissions=user[1].permissions,
            )
            for user in await UserService.get_all(session)
        ]
        return users


"""
Postman:

POST: http://localhost:8000/v1/graphql
Body: Form-data
Key|Datatype: Value
operations|Text: {"query": "mutation ($file: Upload!) { uploadFile(file: $file) }", "variables": { "file": null }}
0|File: <choose file>
map|Text: {"0": ["variables.file"]}

Output:
{
    "data": {
        "uploadFile": "File {filename} was successfully uploaded"
    }
}
"""


@strawberry.type
class FileMutation:
    @strawberry.mutation(description="Upload file")
    async def upload_file(self, file: Upload) -> str:
        content = await file.read()
        filename = file.filename

        file_path = MEDIA_USERS_DIR / f"uploaded_{filename}"
        with open(file_path, "wb") as f:
            f.write(content)
        return f"File {filename} was successfully uploaded"


@strawberry.type
class UserMutation:

    @strawberry.mutation(description="Create new user")
    async def register(
        self,
        user: UserInput,
        info: strawberry.Info,
        permissions: Optional[list[str]] = None,
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

        session = info.context["session"]

        created_user = await UserService.create(data, permissions, session)
        return UserSchema(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email,
            is_admin=created_user.is_admin,
            permissions=created_user.permissions,
        )

    @strawberry.mutation(description="User Login")
    async def login(
        self, username: str, password: str, info: strawberry.Info
    ) -> TokenSchema:
        session = info.context["session"]

        user = await UserService.authenticate_user(username, password, session)
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

    @strawberry.mutation(description="Refresh Token")
    async def refresh_token(token: str, info: strawberry.Info) -> TokenSchema:
        try:
            username = UserService.verify_token(token, "refresh_token")
        except TokenExpiredError as e:
            raise GraphQLError(str(e))
        except TokenIsNotValidError as e:
            raise GraphQLError(str(e))
        except TokenTypeIsNotValidError as e:
            raise GraphQLError(str(e))

        session = info.context["session"]
        user = await UserService.get_by_username(username, session)
        if not user:
            raise GraphQLError("Wrong username or password during token refresh")

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

        try:
            access_token = UserService.create_token(
                data=new_access_token, expires_delta=access_token_expires
            )
        except TokenCreationError as e:
            raise GraphQLError(str(e))

        return TokenSchema(access_token=access_token, refresh_token=token)
