import strawberry

from src.api.graphql.user.resolvers import UserQuery, UserMutation, FileMutation


@strawberry.type
class Query(UserQuery):
    pass


@strawberry.type
class Mutation(UserMutation, FileMutation):
    pass
