from fastapi import Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from users.core.exceptions import (
    TokenExpiredError,
    TokenIsNotValidError,
    TokenTypeIsNotValidError,
)
from users.core.entities import UserResponse
from users.core.services import UserService


async def get_session(request: Request) -> AsyncSession:
    db_helper = request.app.state.db_helper
    async for session in db_helper.get_session():
        yield session


async def get_current_user_from_jwt(
    token: str = Depends(APIKeyHeader(name="Authorization", auto_error=False)),
    session: AsyncSession = Depends(get_session),
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


async def context_dependency(
    request: Request,
    current_user: str = Depends(get_current_user_from_jwt),
):
    """
    Context для Strawberry GraphQL.

    В проде/локально: берём сессию через app.state.db_helper.
    В тестах: переопределяется через dependency_overrides.
    """
    # проверяем, есть ли переопределение get_session (тесты)
    override = request.app.dependency_overrides.get(get_session)
    if override:
        async for session in override():
            yield {"request": request, "current_user": current_user, "session": session}
    else:
        db_helper = request.app.state.db_helper
        async for session in db_helper.get_session():
            yield {"request": request, "current_user": current_user, "session": session}
