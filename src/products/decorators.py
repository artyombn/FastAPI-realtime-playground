from functools import wraps

from fastapi import HTTPException
from starlette import status

from src.products.exceptions import ProductNotFoundError, ProductAlreadyExistsError


def handle_product_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ProductNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except ProductAlreadyExistsError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return wrapper
