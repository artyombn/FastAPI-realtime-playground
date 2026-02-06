from collections import OrderedDict

from src.products.exceptions import ProductAlreadyExistsError, ProductNotFoundError
from src.core.product.entities import ProductResponse


class ProductManager:
    """
    CRUD operations for Product model
    """

    def __init__(self):
        self.products = OrderedDict()
        self.last_product_id = 1

    def add(self, product):
        if len(self.products) != 0:
            self.last_product_id = list(self.products)[-1]
            self.last_product_id += 1

            for p in self.products.values():
                if p.name == product.name:
                    raise ProductAlreadyExistsError()

        updated_pr = ProductResponse(
            id=self.last_product_id,
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )

        self.products[self.last_product_id] = updated_pr
        return updated_pr

    def get_by_id(self, product_id):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError()
        return self.products.get(product_id)

    def get_all(self):
        return [product for product in self.products.values()]

    def update(self, product, product_id):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError()
        new_product = ProductResponse(
            id=product_id,
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )
        self.products[product_id] = new_product
        return new_product

    def delete(self, product_id):
        if not self._is_product_exist(product_id):
            raise ProductNotFoundError()
        del self.products[product_id]
        return None

    def _is_product_exist(self, product_id):
        return product_id in self.products.keys()


product_manager = ProductManager()
