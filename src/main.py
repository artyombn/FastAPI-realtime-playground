import strawberry

from fastapi import FastAPI, APIRouter
from starlette.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from src.config.logger import setup_logging
from src.config.settings import MEDIA_DIR
from src.dependencies import context_dependency
from src.api.graphql.resolvers import Query, Mutation
from src.api.rest.product.views import product_router
from src.api.rest.user.views import user_router

setup_logging()

app = FastAPI()
schema = strawberry.Schema(query=Query, mutation=Mutation)

# API routers
api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(product_router)
api_v1_router.include_router(user_router)

# GraphQL routers
graphql_app = GraphQLRouter(
    schema, context_getter=context_dependency, multipart_uploads_enabled=True
)


app.include_router(api_v1_router)
app.include_router(graphql_app, prefix="/v1/graphql")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/")
async def index():
    return {"message": "This is the main Page"}
