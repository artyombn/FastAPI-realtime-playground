from functools import wraps

from fastapi import Depends, HTTPException
from starlette import status

from src.core.user.exceptions import (
    UserAlreadyExistsError,
    UserNotFoundError,
    UserCreationError,
    TokenIsNotValidError,
    TokenExpiredError,
    TokenTypeIsNotValidError,
    TokenCreationError,
    ServiceError,
)
from src.dependencies import get_current_user_from_jwt


def handle_user_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except UserNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except UserAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except (UserCreationError, ServiceError) as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except (TokenIsNotValidError, TokenExpiredError, TokenTypeIsNotValidError) as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
        except TokenCreationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

    return wrapper


def handle_check_permissions(required_permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args, current_user=Depends(get_current_user_from_jwt), **kwargs
        ):
            if current_user is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication Error: User didn't authenticate",
                )
            user_permissions = current_user.permissions
            if not set(required_permissions).issubset(set(user_permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user doesn't have necessary permissions",
                )
            return await func(*args, current_user=current_user, **kwargs)

        return wrapper

    return decorator
