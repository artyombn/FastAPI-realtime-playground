import strawberry

from src.core.user.services import UserService
from src.api.graphql.schemas import UserSchema


@strawberry.type
class Query:

    @strawberry.field(description="Get User query.")
    def user(self, id: int) -> UserSchema:
        user = UserService.get_by_id(id)
        if not user:
            raise ValueError("User not found.")
        return UserSchema(
            id=id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            permissions=user.permissions,
        )

    @strawberry.field(description="Get all Users query.")
    def all_users(self) -> list[UserSchema]:
        users = [
            UserSchema(
                id=user[0],
                username=user[1].username,
                email=user[1].email,
                is_admin=user[1].is_admin,
                permissions=user[1].permissions,
            )
            for user in UserService.get_all()
        ]
        return users


# @strawberry.type
# class Mutation:
#
#     @strawberry.field(description="Create a new User query.")
#     def create_user(self):
#         pass
