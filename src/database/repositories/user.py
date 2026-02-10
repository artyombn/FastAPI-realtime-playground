from sqlalchemy.orm import Session
from sqlalchemy import select, Sequence

from src.core.user.entities import CreateUser as CreateUserSchema
from src.database.base import SessionLocal
from src.database.models.user import User as UserModel


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_username(self, username: str) -> UserModel | None:
        query = select(UserModel).filter_by(username=username)
        user = self.session.execute(query)
        return user.scalar_one_or_none()

    def get_all(self) -> Sequence[UserModel]:
        query = select(UserModel)
        users = self.session.execute(query)
        return users.scalars().all()

    def add(self, user_data: CreateUserSchema):
        user = UserModel(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin,
        )
        self.session.add(user)
        self.session.commit()
        return user


user_repository = UserRepository(SessionLocal())
