from fastapi import APIRouter
from .managers import product_manager
from .schema import ProductListOutput, ProductOutput, ProductCreate, ProductUpdate

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get(
    "/",
    response_model=ProductListOutput,
    summary="Get list of products",
    description="Returns a list of all products with the total number of items.",
)
async def get_product_list() -> ProductListOutput:
    all_products = product_manager.get_all_products()
    result = ProductListOutput(
        total_products=len(all_products),
        products=all_products,
    )
    return result


@product_router.get(
    "/{product_id}",
    summary="Get product by ID",
    description="Returns detailed information about a product by its unique identifier.",
)
async def get_product_by_product_id(product_id: int) -> ProductOutput:
    product = product_manager.get_product_by_id(product_id)
    result = ProductOutput(
        id=product.id,
        name=product.name,
        quantity=product.quantity,
        price=product.price,
    )
    return result


@product_router.post(
    "/create",
    summary="Create a new product",
    description="Creates a new product and returns the created product with an assigned ID.",
)
async def create_product(product: ProductCreate) -> ProductOutput:
    product = product_manager.add_product(product)
    return product


@product_router.patch(
    "/{product_id}",
    summary="Update product",
    description="Updates an existing product by its ID using partial data.",
)
async def update_product(product: ProductUpdate, product_id: int) -> ProductOutput:
    updated_product = product_manager.update_product(product, product_id)
    return updated_product


@product_router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Deletes a product by its unique identifier.",
)
async def delete_product(product_id: int) -> dict:
    product_manager.delete_product(product_id)
    return {"message": "Product deleted"}
