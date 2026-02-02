from pydantic import BaseModel, Field

class ProductBase(BaseModel):
    """
    Base Product schema for all Products
    """

    name: str = Field(
        min_length=3,
        max_length=100,
        description="Product name must be between 3 and 100 characters",
    )
    quantity: int = Field(
        ge=0,
        description="Product quantity must be int and >= 0"
    )
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

class ProductOutput(ProductBase):
    """
    Schema for getting an existing Product
    """
    id: int = Field(description="Unique pet ID")

class ProductListOutput(BaseModel):
    """
    Schema for getting a list of Products
    """
    total_products: int
    products: list[ProductOutput]
