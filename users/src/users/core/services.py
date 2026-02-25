import logging
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Optional

import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from users.database.uow import unit_of_work

from users.database.repositories.user import UserRepository
from users.core.exceptions import (
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from users.core.entities import (
    UserResponse,
    UserResponseWithHashedPWD,
    CreateUser,
    AdminUser,
    RegularUser,
)

logger = logging.getLogger("fastapi-app")

load_dotenv()

SECRET_KEY: str = os.environ["SECRET_KEY"]
ALGORITHM: str = os.environ["ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.environ["REFRESH_TOKEN_EXPIRE_MINUTES"])


class TokenData(BaseModel):
    sub: str
    is_admin: Optional[bool] = False
    extra: Optional[dict] = Field(default_factory=dict)


class UserService:
    """
    User Service for token creation/update and authorization
    """

    @classmethod
    async def create(
        cls,
        user: CreateUser,
        permissions: Optional[list[str]],
        session: AsyncSession,
    ) -> UserResponse:
        if await UserRepository.get_by_username(
            session=session, username=user.username
        ):
            logger.error(
                f"Attempt to create existed user. username={user.username}, email={user.email}"
            )
            raise UserAlreadyExistsError()

        hashed_password = bcrypt.hashpw(
            user.password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        user.password = hashed_password

        if user.is_admin:
            new_user = AdminUser(
                username=user.username,
                password=user.password,
                email=user.email,
            )
        else:
            new_user = RegularUser(
                username=user.username,
                password=user.password,
                email=user.email,
                permissions=permissions,
            )

        async with unit_of_work(session) as uow:
            # if user.is_admin:
            #     another_user = AdminUser(
            #         username="kolia",
            #         password=user.password,
            #         email="kolia@gmail.com",
            #     )
            # else:
            #     another_user = RegularUser(
            #         username="kolia",
            #         password=user.password,
            #         email="kolia@gmail.com",
            #         permissions=permissions,
            #     )
            # await UserRepository.create(session=uow.session, user_data=another_user)
            user_orm = await UserRepository.create(
                session=uow.session, user_data=new_user
            )
            user_schema = UserResponse.model_validate(user_orm)
        return user_schema

    @classmethod
    async def get_by_id(
        cls, user_id: int, session: AsyncSession
    ) -> UserResponse | None:
        user_orm = await UserRepository.get_by_id(session=session, user_id=user_id)
        if user_orm is None:
            raise UserNotFoundError()
        return UserResponse.model_validate(user_orm)

    @classmethod
    async def get_by_username(
        cls, username: str, session: AsyncSession
    ) -> UserResponse | None:
        user_orm = await UserRepository.get_by_username(
            session=session, username=username
        )
        if user_orm is None:
            raise UserNotFoundError()
        return UserResponse.model_validate(user_orm)

    @classmethod
    async def get_by_username_with_pwd(
        cls, username: str, session: AsyncSession
    ) -> UserResponseWithHashedPWD | None:
        user_orm = await UserRepository.get_by_username(
            session=session, username=username
        )

        if user_orm is None:
            return None
        return UserResponseWithHashedPWD.model_validate(user_orm)

    @classmethod
    async def get_all(cls, session: AsyncSession) -> list[UserResponse]:
        users = await UserRepository.get_all(session)
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @classmethod
    async def authenticate_user(
        cls, username: str, password: str, session: AsyncSession
    ) -> UserResponseWithHashedPWD | None:
        user = await cls.get_by_username_with_pwd(username, session)

        if not user:
            return None

        if not cls.verify_password(password, user.password):
            return None

        return user

    @staticmethod
    def create_token(data: TokenData, expires_delta: timedelta) -> str:
        try:
            expire = datetime.now(timezone.utc) + expires_delta
            payload = data.model_dump(exclude_unset=True)
            payload.update({"exp": int(expire.timestamp())})
            encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        except Exception:
            raise TokenCreationError()
        else:
            return encoded_jwt

    @classmethod
    async def get_current_user_from_jwt(
        cls, token: str, session: AsyncSession
    ) -> UserResponse | None:
        username = cls.verify_token(token, "access_token")
        return await cls.get_by_username(username, session)

    @staticmethod
    def verify_token(token: str, token_type: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            raise TokenExpiredError()
        except JWTError:
            raise TokenIsNotValidError()

        exp = payload.get("exp")
        current_token_type = payload["extra"]["type"]

        if current_token_type != token_type:
            raise TokenTypeIsNotValidError()

        if not exp or datetime.now(timezone.utc) > datetime.fromtimestamp(
            exp, tz=timezone.utc
        ):
            raise TokenExpiredError()

        username = payload.get("sub")

        return username
