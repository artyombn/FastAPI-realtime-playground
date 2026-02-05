from fastapi import APIRouter, HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from .exceptions import ProductAlreadyExistsError, ProductNotFoundError
from .schema import ProductListOutput, ProductOutput, ProductCreate, ProductUpdate
from .services import product_service

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get(
    "/",
    response_model=ProductListOutput,
    summary="Get list of products",
    description="Returns a list of all products with the total number of items.",
)
async def get_product_list() -> ProductListOutput:
    all_products = product_service.get_all()
    products_list_output = ProductListOutput(
        total_products=len(all_products),
        products=all_products,
    )
    return products_list_output


@product_router.get(
    "/{product_id}",
    summary="Get product by ID",
    description="Returns detailed information about a product by its unique identifier.",
)
async def get_product_by_product_id(product_id: int) -> ProductOutput:
    try:
        product_output = product_service.get(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    return product_output


@product_router.post(
    "/create",
    summary="Create a new product",
    description="Creates a new product and returns the created product with an assigned ID.",
)
async def create_product(product: ProductCreate) -> ProductOutput:
    try:
        created_product = product_service.add(product)
    except ProductAlreadyExistsError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    return created_product


@product_router.patch(
    "/{product_id}",
    summary="Update product",
    description="Updates an existing product by its ID using partial data.",
)
async def update_product(product: ProductUpdate, product_id: int) -> ProductOutput:
    try:
        updated_product = product_service.update(product, product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    return updated_product


@product_router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Deletes a product by its unique identifier.",
)
async def delete_product(product_id: int) -> dict:
    try:
        product_service.delete(product_id)
    except ProductNotFoundError as e:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    return {"message": "Product deleted successfully"}
