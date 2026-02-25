from fastapi import APIRouter

from products.core.entities import (
    ProductListResponse,
    ProductResponse,
    ProductCreate,
)
from products.core.services import product_service

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get(
    "/",
    response_model=ProductListResponse,
    summary="Get list of products",
    description="Returns a list of all products with the total number of items.",
)
async def get_product_list() -> ProductListResponse:
    all_products = product_service.list()
    products_list_output = ProductListResponse(
        total_products=len(all_products),
        products=all_products,
    )
    return products_list_output


@product_router.post(
    "/create",
    response_model=dict,
    summary="Create a new product",
    description="Creates a new product and returns the created product with an assigned ID.",
)
async def create_product(
    product: ProductCreate,
) -> dict[str, str]:
    created_product = product_service.add(product)
    return {"result": f"Product {created_product.name} was created successfully"}


@product_router.get(
    "/{product_id}",
    summary="Get product by ID",
    description="Returns detailed information about a product by its unique identifier.",
)
async def get_product_by_product_id(product_id: int) -> ProductResponse:
    product_output = product_service.get_by_id(product_id)
    return product_output


@product_router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Deletes a product by its unique identifier.",
)
async def delete_product(product_id: int) -> dict:
    product_service.delete(product_id)
    return {"message": f"Product was deleted successfully"}
