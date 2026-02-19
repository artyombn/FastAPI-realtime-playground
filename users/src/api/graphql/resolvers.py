import strawberry

from src.api.graphql.product.resolvers import ProductQuery
from src.api.graphql.user.resolvers import UserQuery, UserMutation, FileMutation


@strawberry.type
class Query(UserQuery, ProductQuery):
    pass


@strawberry.type
class Mutation(UserMutation, FileMutation):
    pass
