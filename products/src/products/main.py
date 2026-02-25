from fastapi import FastAPI, APIRouter

from products.api.rest.views import product_router

app = FastAPI()
# API routers
api_v1_router = APIRouter(prefix="/v1/api")
api_v1_router.include_router(product_router)

app.include_router(api_v1_router)


@app.get("/")
async def index():
    return {"message": "This is the main Page"}
