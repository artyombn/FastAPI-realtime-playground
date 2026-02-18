from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_helper import db_helper
from src.core.user.exceptions import (
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from src.core.user.entities import UserResponse
from src.core.user.services import UserService


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


def context_dependency(current_user: str = Depends(get_current_user_from_jwt)) -> dict:
    return {"current_user": current_user}
