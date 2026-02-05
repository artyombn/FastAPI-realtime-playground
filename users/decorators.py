from functools import wraps

from fastapi import Depends, HTTPException
from starlette import status

from users.dependencies import get_current_user_from_jwt


def handle_check_permissions(required_permissions: list[str]):
    def decorator(func):
        @wraps(func)
        async def wrapper(
            *args, current_user=Depends(get_current_user_from_jwt), **kwargs
        ):
            user_permissions = current_user.permissions
            if not set(required_permissions).issubset(set(user_permissions)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This user doesn't have necessary permissions",
                )
            return await func(*args, current_user, **kwargs)

        return wrapper

    return decorator
