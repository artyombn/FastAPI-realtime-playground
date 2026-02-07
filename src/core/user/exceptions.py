class UserAlreadyExistsError(Exception):
    def __init__(self, message: str = "User already exists"):
        super().__init__(message)


class UserNotFoundError(Exception):
    def __init__(self, message: str = "User not found"):
        super().__init__(message)


class UserCreationError(Exception):
    def __init__(self, message: str = "User creation failed"):
        super().__init__(message)


class TokenIsNotValidError(Exception):
    def __init__(self, message: str = "Authentication Error: Token is not valid"):
        super().__init__(message)


class TokenExpiredError(Exception):
    def __init__(self, message: str = "Authentication Error: Token is expired"):
        super().__init__(message)


class TokenTypeIsNotValidError(Exception):
    def __init__(self, message: str = "Authentication Error: Token type is not valid"):
        super().__init__(message)


class TokenCreationError(Exception):
    def __init__(self, message: str = "Authentication Error: Error creating token"):
        super().__init__(message)
