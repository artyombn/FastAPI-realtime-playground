class UserAlreadyExistsError(Exception):
    pass


class UserNotFoundError(Exception):
    pass


class UserCreationError(Exception):
    pass


class TokenIsNotValidError(Exception):
    pass


class TokenExpiredError(Exception):
    pass


class TokenTypeIsNotValidError(Exception):
    pass


class TokenCreationError(Exception):
    pass
