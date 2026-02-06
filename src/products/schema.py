from pydantic import BaseModel, Field

from src.users.schema import UserResponse


class ProductBase(BaseModel):
    """
    Base Product schema for all Products
    """

    name: str = Field(
        min_length=3,
        max_length=100,
        description="Product name must be between 3 and 100 characters",
    )
    quantity: int = Field(ge=0, description="Product quantity must be int and >= 0")
    price: float = Field(
        gt=0.0,
        le=9999999.0,
        description="Product price must be float, >= 0.0 and <= 9999999.0",
    )


class ProductCreate(ProductBase):
    """
    Schema for creating a new Product
    """


class ProductUpdate(ProductBase):
    """
    Schema for updating an existing Product
    """


class ProductDelete(ProductBase):
    """
    Schema for deleting an existing Product
    """


class ProductResponse(ProductBase):
    """
    Schema for getting an existing Product
    """

    id: int = Field(description="Unique product ID")


class ProductListResponse(BaseModel):
    """
    Schema for getting a list of Products
    """

    total_products: int
    products: list[ProductResponse]


class CreateProductResponse(BaseModel):
    """
    Response schema for created Product with appropriate information (product, user)
    """

    created_product: ProductResponse
    user_who_created: UserResponse


class UpdateProductResponse(BaseModel):
    """
    Response schema for updated Product with appropriate information (product, user)
    """

    updated_product: ProductResponse
    user_who_updated: UserResponse
