from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from src.core.user.exceptions import (
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from src.core.user.entities import UserResponse
from src.core.user.services import UserService


def get_current_user_from_jwt(
    token: str = Depends(APIKeyHeader(name="Authorization")),
) -> UserResponse | None:
    try:
        user_tuple = UserService.get_current_user_from_jwt(token)
    except TokenExpiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TokenIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TokenTypeIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not user_tuple:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    user_id = user_tuple[0]
    user = user_tuple[1]

    user_output = UserResponse(
        id=user_id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        permissions=user.permissions,
    )

    return user_output
