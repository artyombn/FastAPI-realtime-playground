import strawberry


@strawberry.type
class ProductSchema:
    id: int
    name: str
    quantity: int
    price: float


@strawberry.type
class ProductPage:
    items: list[ProductSchema]
    total_items: int
    offset: int
    limit: int
