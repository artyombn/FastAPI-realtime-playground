from functools import wraps


def require_authentication(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        info = kwargs.get("info") or args[1]
        current_user = info.context.get("current_user")
        if not current_user:
            raise ValueError("Authentication required")

        return func(*args, **kwargs)

    return wrapper
