import logging

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user import UserORM
from src.core.user.services import UserService
from src.core.permissions import Permissions
from src.core.user.entities import CreateUser

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio()
async def test_add_user(db_session: AsyncSession, patch_uow):
    user = CreateUser(
        username="test_user_service",
        email="test_user_service@gmail.com",
        password="MyCat@Barsik7",
        is_admin=False,
    )
    log.debug(f"USER_SERVICE = {user}")

    created_user = await UserService.create(
        user=user,
        permissions=[Permissions.VIEW_PRODUCT, Permissions.DELETE_PRODUCT],
        session=db_session,
    )
    log.debug(f"CREATED_USER = {created_user}")

    stmt = select(UserORM).where(UserORM.username == "test_user_service")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()
    log.debug(f"FOUND_SERVICE = {found}")

    assert found is not None
    assert found.username == "test_user_service"
    assert found.email == "test_user_service@gmail.com"
