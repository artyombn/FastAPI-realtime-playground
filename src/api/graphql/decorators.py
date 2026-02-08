from functools import wraps

from src.api.graphql.user.schemas import UserPage


def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = kwargs.get("info") or args[1]
        current_user = info.context.get("current_user")
        if not current_user:
            raise ValueError("Authentication required")

        return func(*args, **kwargs)

    return wrapper


def paginate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        limit = kwargs["limit"] or 10
        offset = kwargs["offset"] or 0
        all_items = func(*args, **kwargs)
        total_items = len(all_items)
        paginated_items = list(all_items)[offset : offset + limit]
        return UserPage(
            items=paginated_items, total_items=total_items, offset=offset, limit=limit
        )

    return wrapper
