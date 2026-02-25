import strawberry

from users.api.graphql.user.resolvers import UserQuery, UserMutation, FileMutation


@strawberry.type
class Query(UserQuery):
    pass


@strawberry.type
class Mutation(UserMutation, FileMutation):
    pass
