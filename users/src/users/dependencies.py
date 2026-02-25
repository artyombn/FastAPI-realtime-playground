from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from users.core.exceptions import (
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from src.core.entities import UserResponse
from src.core.services import UserService
from users.core.entities import UserResponse
from users.core.services import UserService


async def get_current_user_from_jwt(
    token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    session: AsyncSession = Depends(db_helper.get_session),
) -> UserResponse | None:
    if not token:
        return None
    try:
        user = await UserService.get_current_user_from_jwt(token, session)
    except TokenExpiredError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TokenIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except TokenTypeIsNotValidError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )

    return UserResponse.model_validate(user)


async def require_admin(
    current_user=Depends(get_current_user_from_jwt),
):
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication Error: User didn't authenticate",
        )

    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This user doesn't have necessary permissions",
        )

    return current_user


def context_dependency(
    current_user: str = Depends(get_current_user_from_jwt),
    session: AsyncSession = Depends(db_helper.get_session),
) -> dict:
    return {"current_user": current_user, "session": session}
