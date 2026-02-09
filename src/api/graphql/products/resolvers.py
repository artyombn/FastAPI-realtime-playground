import strawberry

from src.api.graphql.decorators import require_authentication, paginate
from src.api.graphql.products.schemas import ProductPage, ProductSchema
from src.core.product.services import ProductService


@strawberry.type
class ProductQuery:

    @strawberry.field(description="Get all products")
    @require_authentication
    @paginate(entity="product")
    def all_products(self, info, limit: int, offset: int) -> ProductPage:
        products = [
            ProductSchema(
                id=product.id,
                name=product.name,
                quantity=product.quantity,
                price=product.price,
            )
            for product in ProductService.get_all()
        ]
        return products
