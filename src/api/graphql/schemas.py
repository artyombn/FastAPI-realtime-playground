import strawberry


@strawberry.type
class UserSchema:
    id: int
    username: str
    email: str
