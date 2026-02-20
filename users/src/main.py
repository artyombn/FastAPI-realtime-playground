from contextlib import asynccontextmanager

import strawberry

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from strawberry.fastapi import GraphQLRouter

from src.database.db_helper import db_helper
from src.config.logger import setup_logging
from src.config.paths import MEDIA_USERS_DIR

from src.dependencies import context_dependency
from src.api.graphql.resolvers import Query, Mutation
from src.api.rest.views import user_router

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):

    yield

    await db_helper.dispose()


app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

schema = strawberry.Schema(query=Query, mutation=Mutation)
# API routers
api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(user_router)

# GraphQL routers
graphql_app = GraphQLRouter(
    schema, context_getter=context_dependency, multipart_uploads_enabled=True
)


app.include_router(api_v1_router)
app.include_router(graphql_app, prefix="/v1/graphql")
app.mount("/media", StaticFiles(directory=MEDIA_USERS_DIR), name="media")


@app.get("/")
async def index():
    return {"message": "This is the main Page"}
