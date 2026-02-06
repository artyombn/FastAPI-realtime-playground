class UserAlreadyExistsError(Exception):
    def __init__(self):
        super().__init__("User already exists")


class UserNotFoundError(Exception):
    def __init__(self):
        super().__init__("User not found")


class UserCreationError(Exception):
    def __init__(self):
        super().__init__("User creation failed")


class TokenIsNotValidError(Exception):
    def __init__(self):
        super().__init__("Authentication Error: Token is not valid")


class TokenExpiredError(Exception):
    def __init__(self):
        super().__init__("Authentication Error: Token is expired")


class TokenTypeIsNotValidError(Exception):
    def __init__(self):
        super().__init__("Authentication Error: Token type is not valid")


class TokenCreationError(Exception):
    def __init__(self):
        super().__init__("Authentication Error: Error creating token")
