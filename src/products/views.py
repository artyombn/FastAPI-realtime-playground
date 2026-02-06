from fastapi import APIRouter, Depends

from src.users.decorators import handle_check_permissions
from src.users.dependencies import get_current_user_from_jwt
from src.users.permissions import Permissions
from src.users.schema import UserResponse
from .decorators import handle_product_errors
from .schema import (
    ProductListResponse,
    ProductResponse,
    ProductCreate,
    ProductUpdate,
    UpdateProductResponse,
    CreateProductResponse,
)
from .services import product_service

product_router = APIRouter(prefix="/products", tags=["products"])


@product_router.get(
    "/",
    response_model=ProductListResponse,
    summary="Get list of products",
    description="Returns a list of all products with the total number of items.",
)
@handle_check_permissions([Permissions.VIEW_PRODUCT])
async def get_product_list(
    current_user=Depends(get_current_user_from_jwt),
) -> ProductListResponse:
    all_products = product_service.get_all()
    products_list_output = ProductListResponse(
        total_products=len(all_products),
        products=all_products,
    )
    return products_list_output


@product_router.get(
    "/{product_id}",
    summary="Get product by ID",
    description="Returns detailed information about a product by its unique identifier.",
)
@handle_check_permissions([Permissions.VIEW_PRODUCT])
@handle_product_errors
async def get_product_by_product_id(
    product_id: int, current_user=Depends(get_current_user_from_jwt)
) -> ProductResponse:
    product_output = product_service.get(product_id)
    return product_output


@product_router.post(
    "/create",
    response_model=CreateProductResponse,
    summary="Create a new product",
    description="Creates a new product and returns the created product with an assigned ID.",
)
@handle_check_permissions([Permissions.ADD_PRODUCT])
@handle_product_errors
async def create_product(
    product: ProductCreate,
    current_user=Depends(get_current_user_from_jwt),
) -> CreateProductResponse:
    created_product = product_service.add(product)
    return CreateProductResponse(
        created_product=created_product, user_who_created=current_user
    )


@product_router.patch(
    "/{product_id}",
    response_model=UpdateProductResponse,
    summary="Update product",
    description="Updates an existing product by its ID using partial data.",
)
@handle_check_permissions([Permissions.UPDATE_PRODUCT])
@handle_product_errors
async def update_product(
    product: ProductUpdate,
    product_id: int,
    current_user=Depends(get_current_user_from_jwt),
) -> UpdateProductResponse:
    updated_product = product_service.update(product, product_id)
    return UpdateProductResponse(
        updated_product=updated_product, user_who_updated=current_user
    )


@product_router.delete(
    "/{product_id}",
    summary="Delete product",
    description="Deletes a product by its unique identifier.",
)
@handle_check_permissions([Permissions.DELETE_PRODUCT])
@handle_product_errors
async def delete_product(
    product_id: int,
    current_user=Depends(get_current_user_from_jwt),
) -> dict:
    product_service.delete(product_id)
    return {"message": f"Product was deleted successfully by {current_user.username}"}
