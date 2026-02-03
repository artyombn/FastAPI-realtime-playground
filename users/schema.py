from pydantic import BaseModel, Field, EmailStr

PERMISSIONS = ["view_product", "update_product", "add_product", "delete_product"]


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
    permissions: list[str] = []


class AdminUser(UserBase):
    """
    Schema for creating a new Admin user

    DEFAULT VALUES:
        is_admin = True
        permissions = ["view_product", "update_product", "add_product", "delete_product"]
    """

    is_admin: bool = True
    permissions: list[str] = PERMISSIONS


class RegularUser(UserBase):
    """
    Schema for creating a new Regular user

    DEFAULT VALUES:
        is_admin = False
        permissions = []
    """

    is_admin: bool = False


class UserOutput(UserBase):
    """
    Schema for getting an existing User
    """

    id: int = Field(description="Unique user ID")


class UserListOutput(BaseModel):
    total_users: int
    users: list[UserOutput]
