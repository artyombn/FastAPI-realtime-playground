from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
import os
from typing import Optional

import bcrypt
from jose import jwt, JWTError, ExpiredSignatureError
from pydantic import BaseModel, Field

from users.exceptions import (
    TokenCreationError,
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from users.managers import user_manager
from users.schema import (
    UserOutput,
    UserOutputWithHashedPWD,
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

    @staticmethod
    def add(user: CreateUser, permissions: Optional[list[str]]) -> UserOutput:
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

        return user_manager.add(new_user)

    @staticmethod
    def get_by_id(user_id: int) -> UserOutput:
        user_output = user_manager.get_by_id(user_id)
        return user_output

    @staticmethod
    def get_by_username(username: str) -> UserOutput | None:
        user_output = user_manager.get_by_username(username)
        return user_output

    @staticmethod
    def get_all() -> list[UserOutput]:
        return user_manager.get_all()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @classmethod
    def authenticate_user(
        cls, username: str, password: str
    ) -> UserOutputWithHashedPWD | None:
        user_tuple = user_manager.get_by_username(username)

        if not user_tuple:
            return None

        user_id = user_tuple[0]
        user = user_tuple[1]
        if not cls.verify_password(password, user.password):
            return None
        user_output = UserOutputWithHashedPWD(
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
            raise TokenCreationError("Error creating token")
        else:
            return encoded_jwt

    @classmethod
    def get_current_user_from_jwt(cls, token: str) -> UserOutput | None:
        username = cls.verify_token(token, "access_token")
        return cls.get_by_username(username)

    @staticmethod
    def verify_token(token: str, token_type: str) -> str:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        except ExpiredSignatureError:
            raise TokenExpiredError("Token expired")
        except JWTError:
            raise TokenIsNotValidError("Token is not valid")

        exp = payload.get("exp")
        current_token_type = payload["extra"]["type"]

        if current_token_type != token_type:
            raise TokenTypeIsNotValidError("Token type is not valid")

        if not exp or datetime.now(timezone.utc) > datetime.fromtimestamp(
            exp, tz=timezone.utc
        ):
            raise TokenExpiredError("Token expired")

        username = payload.get("sub")

        return username
