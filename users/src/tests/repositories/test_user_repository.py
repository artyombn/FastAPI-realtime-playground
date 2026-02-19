import logging

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.user.entities import CreateUser as CreateUserSchema
from src.database.repositories.user import UserRepository
from src.database.models.user import UserORM

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_add_user(db_session: AsyncSession):
    user = CreateUserSchema(
        username="test_user_repository",
        email="test_user_repository@gmail.com",
        password="MyCat@Barsik7",
        is_admin=False,
    )
    log.debug(f"USER_REPOSITORY = {user}")

    res = await UserRepository.create(db_session, user)
    log.debug(f"RES_REPOSITORY = {res}")

    stmt = select(UserORM).where(UserORM.username == "test_user_repository")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.username == "test_user_repository"
    assert found.email == "test_user_repository@gmail.com"

    await db_session.rollback()
