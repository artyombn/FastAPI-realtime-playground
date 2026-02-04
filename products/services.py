from products.managers import product_manager, ProductManager
from products.schema import ProductOutput, ProductCreate, ProductUpdate


class ProductService:
    """
    Product Service to manage products
    """

    def __init__(self, manager: ProductManager):
        self.manager = manager

    def add(self, product: ProductCreate) -> ProductOutput:
        return self.manager.add(product)

    def get(self, product_id: int) -> ProductOutput:
        return self.manager.get_by_id(product_id)

    def update(self, product: ProductUpdate, product_id: int) -> ProductOutput:
        return self.manager.update(product, product_id)

    def delete(self, product_id: int) -> dict:
        self.manager.delete(product_id)
        return {"message": "Product deleted successfully"}

    def get_all(self) -> list[ProductOutput]:
        return self.manager.get_all()


product_service = ProductService(product_manager)
