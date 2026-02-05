from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader

from users.exceptions import (
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from users.schema import UserOutput
from users.services import UserService


def get_current_user_from_jwt(
    token: str = Depends(APIKeyHeader(name="Authorization")),
) -> UserOutput | None:
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

    user_output = UserOutput(
        id=user_id,
        username=user.username,
        email=user.email,
        is_admin=user.is_admin,
        permissions=user.permissions,
    )

    return user_output


def check_permissions(required_permissions: list[str]):
    def permission_dependency(current_user=Depends(get_current_user_from_jwt)):
        user_permissions = current_user.permissions
        if not set(required_permissions).issubset(set(user_permissions)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User doesn't have necessary permissions",
            )
        return current_user

    return permission_dependency
