class ProductAlreadyExistsError(Exception):
    def __init__(self, message: str = "Product already exists"):
        super().__init__(message)


class ProductNotFoundError(Exception):
    def __init__(self, message: str = "Product not found"):
        super().__init__(message)
