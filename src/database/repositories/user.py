from sqlalchemy.orm import Session
from sqlalchemy import select, Sequence

from src.core.user.entities import CreateUser as CreateUserSchema
from src.database.models.user import UserORM


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> UserORM | None:
        query = select(UserORM).filter_by(username=username)
        user = self.session.execute(query)
        return user.scalar_one_or_none()

    def get_by_id(self, user_id: int) -> UserORM | None:
        query = select(UserORM).filter_by(id=user_id)
        user = self.session.execute(query)
        return user.scalar_one_or_none()

    def get_all(self) -> Sequence[UserORM]:
        query = select(UserORM)
        users = self.session.execute(query)
        return users.scalars().all()

    def add(self, user_data: CreateUserSchema):
        user = UserORM(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin,
        )
        self.session.add(user)
        self.session.flush()
        return user


def user_repository_factory(session: Session):
    return UserRepository(session)
