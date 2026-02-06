import string

from pydantic import BaseModel, Field, EmailStr, field_validator

from src.core.permissions import Permissions


class UserBase(BaseModel):
    """
    Base User schema for all users models
    """

    username: str = Field(
        min_length=3,
        max_length=100,
        description="Username must be between 3 and 100 characters",
    )
    email: EmailStr = Field(description="Use a valid email")
    is_admin: bool = False
    permissions: list[str] = Field(default_factory=list)


class CreateUser(UserBase):
    """
    Schema for creating a new user
    Extra field: password with validation (has_letter/has_digit/has_symbol/has_upper)
    """

    password: str = Field(
        min_length=8,
        max_length=100,
    )

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        has_letter = False
        has_digit = False
        has_symbol = False
        has_upper = False

        for v in value:
            if v.isalpha():
                has_letter = True
            if v.isdigit():
                has_digit = True
            if v in string.punctuation:
                has_symbol = True
            if v.isupper():
                has_upper = True
        if not (has_letter and has_digit and has_symbol and has_upper):
            raise ValueError(
                "Incorrect password.\n"
                "Password must contain at least one letter, one digit, one uppercase letter and one special symbol"
            )

        return value


class AdminUser(CreateUser):
    """
    Schema for creating a new Admin user

    DEFAULT VALUES:
        is_admin = True
        permissions = ["view_product", "update_product", "add_product", "delete_product"]
    """

    is_admin: bool = True
    permissions: list[str] = Permissions.list()


class RegularUser(CreateUser):
    """
    Schema for creating a new Regular user

    DEFAULT VALUES:
        is_admin = False
        permissions = []
    """

    is_admin: bool = False


class UserResponse(UserBase):
    """
    Schema for getting an existing User
    """

    id: int = Field(description="Unique user ID")


class UserResponseWithHashedPWD(UserResponse):
    """
    To get an existing User with hashed password
    """

    password: str = Field(description="Hashed User Password")


class UserListResponse(BaseModel):
    """
    To get a list all Users with total number
    """

    total_users: int
    users: list[UserResponse]
