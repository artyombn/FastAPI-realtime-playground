from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Sequence

from users.core.entities import CreateUser as CreateUserSchema
from users.database.models.user import UserORM


class UserRepository:
    @classmethod
    async def get_by_username(
        cls, session: AsyncSession, username: str
    ) -> UserORM | None:
        query = select(UserORM).filter_by(username=username)
        user = await session.execute(query)
        return user.scalar_one_or_none()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int) -> UserORM | None:
        query = select(UserORM).filter_by(id=user_id)
        user = await session.execute(query)
        return user.scalar_one_or_none()

    @classmethod
    async def get_all(cls, session: AsyncSession) -> Sequence[UserORM]:
        query = select(UserORM)
        users = await session.execute(query)
        return users.scalars().all()

    @classmethod
    async def create(cls, session: AsyncSession, user_data: CreateUserSchema):
        user = UserORM(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            is_admin=user_data.is_admin,
            permissions=user_data.permissions,
        )
        session.add(user)
        await session.flush()
        return user
