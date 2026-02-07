import strawberry

from fastapi import FastAPI, APIRouter
from strawberry.fastapi import GraphQLRouter

from src.api.graphql.resolvers import Query
from src.api.rest.product.views import product_router
from src.api.rest.user.views import user_router

app = FastAPI()
schema = strawberry.Schema(query=Query)

# API routers
api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(product_router)
api_v1_router.include_router(user_router)

# GraphQL routers
graphql_app = GraphQLRouter(schema)


app.include_router(api_v1_router)
app.include_router(graphql_app, prefix="/v1/graphql")


@app.get("/")
async def index():
    return {"message": "This is the main Page"}
