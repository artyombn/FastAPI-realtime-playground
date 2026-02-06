from fastapi import FastAPI, APIRouter

from src.api.rest.product.views import product_router
from src.api.rest.user.views import user_router

app = FastAPI()

api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(product_router)
api_v1_router.include_router(user_router)

app.include_router(api_v1_router)


@app.get("/")
async def index():
    return {"message": "This is the main Page"}
