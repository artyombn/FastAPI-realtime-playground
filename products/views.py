from fastapi import APIRouter

product_router = APIRouter(
    prefix="/products",
    tags=["products"]
)

@product_router.get("/")
async def get_product_list():
    return {"message": "This is a list of Products"}

