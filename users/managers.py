from collections import OrderedDict
from fastapi import HTTPException

from users.schema import UserOutput


class UserManager:
    """
    CRUD operations for User model
    """

    def __init__(self):
        self.users = OrderedDict()
        self.last_user_id = 1

    def add_user(self, user):
        if len(self.users) != 0:
            self.last_user_id = list(self.users)[-1]
            self.last_user_id += 1

        updated_user = UserOutput(
            id=self.last_user_id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            permissions=user.permissions,
        )
        self.users[self.last_user_id] = updated_user
        return updated_user

    def get_user_by_user_id(self, user_id: int):
        print(f"user with ID={user_id} found")
        print(f"IT IS IN USERS {self._is_user(user_id)}")
        if not self._is_user(user_id):
            raise HTTPException(
                status_code=404, detail=f"User with ID={user_id} not found"
            )
        return self.users.get(user_id)

    def get_all_users(self):
        return list(self.users.values())

    def _is_user(self, user_id: int):
        return user_id in self.users.keys()


user_manager = UserManager()
