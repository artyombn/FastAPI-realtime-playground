import strawberry

from src.api.graphql.user.resolvers import UserQuery, UserMutation


@strawberry.type
class Query(UserQuery):
    pass


@strawberry.type
class Mutation(UserMutation):
    pass
