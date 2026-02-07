import strawberry


@strawberry.type
class UserSchema:
    id: int
    username: str
    email: str
    is_admin: bool
    permissions: list[str]


@strawberry.type
class TokenSchema:
    access_token: str
    refresh_token: str
