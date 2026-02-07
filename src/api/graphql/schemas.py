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


@strawberry.input
class UserInput:
    username: str
    email: str
    password: str
    is_admin: bool = False
    permissions: list[str] = strawberry.field(default_factory=list)
