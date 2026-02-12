from sqlalchemy.orm import Session
from sqlalchemy import select, Sequence

from src.core.user.entities import CreateUser as CreateUserSchema
from src.database.models.user import UserORM


class UserRepository:
    @classmethod
    def get_by_username(cls, session: Session, username: str) -> UserORM | None:
        query = select(UserORM).filter_by(username=username)
        user = session.execute(query)
        return user.scalar_one_or_none()

    @classmethod
    def get_by_id(cls, session: Session, user_id: int) -> UserORM | None:
        query = select(UserORM).filter_by(id=user_id)
        user = session.execute(query)
        return user.scalar_one_or_none()

    @classmethod
    def get_all(cls, session: Session) -> Sequence[UserORM]:
        query = select(UserORM)
        users = session.execute(query)
        return users.scalars().all()

    @classmethod
    def add(cls, session: Session, user_data: CreateUserSchema):
        user = UserORM(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin,
            permissions=user_data.permissions,
        )
        session.add(user)
        session.flush()
        return user
