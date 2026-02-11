from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Optional

import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel, Field

from src.database.base import SessionLocal
from src.database.exceptions import UnitOfWorkError
from src.database.uow import unit_of_work
from src.database.repositories.user import (
    user_repository_factory,
)
from src.database.repositories.user import UserRepository
from src.core.user.exceptions import (
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
    UserAlreadyExistsError,
    ServiceError,
)
from src.core.user.entities import (
    UserResponse,
    UserResponseWithHashedPWD,
    CreateUser,
    AdminUser,
    RegularUser,
)

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

    def __init__(self, repository_factory: UserRepository):
        self.user_repository_factory = repository_factory

    def add(self, user: CreateUser, permissions: Optional[list[str]]) -> UserResponse:
        if self.get_by_username(user.username):
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
        try:
            with unit_of_work() as uow:
                user_repository = self.user_repository_factory(uow.session)

                user_orm = user_repository.add(new_user)

                if user.is_admin:
                    another_user = AdminUser(
                        username="ivan",
                        password=user.password,
                        email="ivan@gmail.com",
                    )
                else:
                    another_user = RegularUser(
                        username="ivan",
                        password=user.password,
                        email="ivan@gmail.com",
                        permissions=permissions,
                    )
                user_repository.add(another_user)
                user_schema = UserResponse.model_validate(user_orm)

        except UnitOfWorkError:
            raise ServiceError()
        return user_schema

    def get_by_id(self, user_id: int) -> UserResponse | None:
        user_repository = self.user_repository_factory(SessionLocal())
        user_orm = user_repository.get_by_id(user_id)
        return UserResponse.model_validate(user_orm)

    def get_by_username(self, username: str) -> UserResponse | None:
        user_repository = self.user_repository_factory(SessionLocal())
        user_orm = user_repository.get_by_username(username)
        return user_orm

    def get_all(self) -> list[UserResponse]:
        user_repository = self.user_repository_factory(SessionLocal())
        users = user_repository.get_all()
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def authenticate_user(
        self, username: str, password: str
    ) -> UserResponseWithHashedPWD | None:
        user_orm = self.get_by_username(username)

        if not user_orm:
            return None

        if not self.verify_password(password, user_orm.password):
            return None

        user_output = UserResponseWithHashedPWD(
            id=user_orm.id,
            username=user_orm.username,
            password=user_orm.password,
            email=user_orm.email,
            is_admin=user_orm.is_admin,
            permissions=user_orm.permissions,
        )
        return user_output

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
    def get_current_user_from_jwt(cls, token: str) -> UserResponse | None:
        username = cls.verify_token(token, "access_token")
        return cls.get_by_username(username)

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


user_service = UserService(user_repository_factory)
