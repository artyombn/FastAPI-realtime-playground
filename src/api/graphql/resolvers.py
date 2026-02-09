import strawberry

from src.api.graphql.product.resolvers import ProductQuery
from src.api.graphql.user.resolvers import UserQuery, UserMutation


@strawberry.type
class Query(UserQuery, ProductQuery):
    pass


@strawberry.type
class Mutation(UserMutation):
    pass
