import strawberry

from src.api.graphql.schemas import UserSchema


@strawberry.type
class Query:

    @strawberry.field(description="Get a graphql query.")
    def user(self, id: int) -> UserSchema:
        users = {
            1: {"id": 1, "username": "Anton", "email": "anton@example.com"},
            2: {"id": 2, "username": "Olga", "email": "olga@example.com"},
        }
        user_data = users.get(id)
        if not user_data:
            raise ValueError("User not found.")
        return UserSchema(**user_data)
