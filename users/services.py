from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from starlette import status

from users.managers import user_manager
from users.schema import UserOutput, UserOutputWithHashedPWD

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

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    @classmethod
    def authenticate_user(
        cls, username: str, password: str
    ) -> UserOutputWithHashedPWD | None:
        user_tuple = user_manager.get_user_by_username(username)
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
        payload = data.model_dump(exclude_unset=True)
        expire = datetime.now() + expires_delta
        payload.update({"exp": expire})
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_current_user_from_jwt(
        token: str = Depends(APIKeyHeader(name="Authorization")),
    ) -> UserOutput | None:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
            username = payload.get("sub")
            user_tuple = user_manager.get_user_by_username(username)

            user_id = user_tuple[0]
            user = user_tuple[1]

            user_output = UserOutput(
                id=user_id,
                username=user.username,
                email=user.email,
                is_admin=user.is_admin,
                permissions=user.permissions,
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
        return user_output
