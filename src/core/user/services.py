from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Optional

import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel, Field

from src.database.repositories.user import UserRepository, user_repository
from src.core.user.exceptions import (
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
    UserAlreadyExistsError,
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

    def __init__(self, repository: UserRepository):
        self.repository = repository

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

        user_orm = self.repository.add(new_user)
        return UserResponse.model_validate(user_orm)

    def get_by_id(self, user_id: int) -> UserResponse | None:
        user_orm = self.repository.get_by_id(user_id)
        return UserResponse.model_validate(user_orm)

    def get_by_username(self, username: str) -> UserResponse | None:
        user_orm = self.repository.get_by_username(username)
        return user_orm

    def get_all(self) -> list[UserResponse]:
        users = self.repository.get_all()
        return [UserResponse.model_validate(user) for user in users]

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    def authenticate_user(
        self, username: str, password: str
    ) -> UserResponseWithHashedPWD | None:
        user_tuple = self.get_by_username(username)

        if not user_tuple:
            return None

        user_id = user_tuple[0]
        user = user_tuple[1]
        if not self.verify_password(password, user.password):
            return None
        user_output = UserResponseWithHashedPWD(
            id=user_id,
            username=user.username,
            password=user.password,
            email=user.email,
            is_admin=user.is_admin,
            permissions=user.permissions,
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


user_service = UserService(user_repository)
