class UnitOfWorkError(Exception):
    def __init__(self, message: str = "Database transaction failed"):
        super().__init__(message)
