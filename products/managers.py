from fastapi import HTTPException
from collections import OrderedDict

from products.schema import ProductOutput


class ProductManager:
    """
    CRUD operations for Product model
    """

    def __init__(self):
        self.products = OrderedDict()

    def add_product(self, product):
        try:
            last_product_id = list(self.products)[-1]
        except Exception:
            last_product_id = 0

        if last_product_id != 0:
            last_product_id += 1
        else:
            last_product_id = 1

        updated_pr = ProductOutput(
            id=last_product_id,
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )

        self.products[last_product_id] = updated_pr
        return updated_pr

    def get_product_by_id(self, product_id):
        if not self._is_product_exist(product_id):
            raise HTTPException(
                status_code=404, detail=f"Product ID={product_id} not found"
            )
        return self.products[product_id]

    def get_all_products(self):
        return [product for product in self.products.values()]

    def update_product(self, product, product_id):
        if not self._is_product_exist(product_id):
            raise HTTPException(
                status_code=404, detail=f"Product ID={product_id} not found"
            )
        new_product = ProductOutput(
            id=product_id,
            name=product.name,
            quantity=product.quantity,
            price=product.price,
        )
        self.products[product_id] = new_product
        return new_product

    def delete_product(self, product_id):
        if not self._is_product_exist(product_id):
            raise HTTPException(
                status_code=404, detail=f"Product ID={product_id} not found"
            )
        del self.products[product_id]
        return None

    def _is_product_exist(self, product_id):
        return product_id in self.products.keys()


product_manager = ProductManager()
