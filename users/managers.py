from collections import OrderedDict

import bcrypt

from users.exceptions import (
    UserAlreadyExistsError,
    UserCreationError,
    UserNotFoundError,
)
from users.schema import UserOutput


class UserManager:
    """
    CRUD operations for User model
    """

    def __init__(self):
        self.users = OrderedDict()
        self.last_user_id = 1

    def add(self, user):
        if len(self.users) != 0:
            self.last_user_id = list(self.users)[-1]
            self.last_user_id += 1

            for u in self.users.values():
                if u.username == user.username:
                    raise UserAlreadyExistsError("User already exists")

        try:
            hashed_password = bcrypt.hashpw(
                user.password.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
            user.password = hashed_password

            self.users[self.last_user_id] = user
            output_user = UserOutput(
                id=self.last_user_id,
                username=user.username,
                email=user.email,
                is_admin=user.is_admin,
                permissions=user.permissions,
            )
        except Exception:
            raise UserCreationError("User creation failed")

        return output_user

    def get_by_id(self, user_id: int):
        if not self._is_user(user_id):
            raise UserNotFoundError("User not found")
        return self.users.get(user_id)

    def get_by_username(self, username: str):
        for user in self.users.items():
            if user[1].username == username:
                return user
        return None

    def get_all(self):
        return list(self.users.items())

    def _is_user(self, user_id: int):
        return user_id in self.users.keys()


user_manager = UserManager()
