from pydantic import BaseModel, Field


class PriceHistory(BaseModel):
    prices: dict[str, float]


class ProductBase(BaseModel):
    """
    Base Product schema for all Products
    """

    id: int = Field(description="Unique product ID")
    name: str = Field(
        min_length=3,
        max_length=100,
        description="Product name must be between 3 and 100 characters",
    )
    quantity: int = Field(ge=0, description="Product quantity must be int and >= 0")
    origin_price: float = Field(
        gt=0.0,
        le=9999999.0,
        description="Product price must be float, >= 0.0 and <= 9999999.0",
    )
    price_history: PriceHistory = Field(
        default_factory=dict, description="Prices history for this product"
    )


class ProductCreate(ProductBase):
    """
    Schema for creating a new Product
    """


class ProductResponse(ProductBase):
    """
    Schema for getting an existing Product
    """


class ProductListResponse(BaseModel):
    """
    Schema for getting a list of Products
    """

    total_products: int
    products: list[ProductResponse]
