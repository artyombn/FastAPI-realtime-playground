import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models.user import UserORM
from src.core.user.services import UserService
from src.core.permissions import Permissions
from src.core.user.entities import CreateUser, UserResponse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test_add_user(db_session: Session):
    user = CreateUser(
        username="test_user_service",
        email="test_user_service@gmail.com",
        password="MyCat@Barsik7",
        is_admin=False,
    )
    log.debug(f"USER_SERVICE = {user}")

    created_user = UserService.add(
        user=user,
        permissions=[Permissions.VIEW_PRODUCT, Permissions.ADD_PRODUCT.DELETE_PRODUCT],
        session=db_session,
    )
    log.debug(f"CREATED_USER = {created_user}")

    query = select(UserORM).filter(UserORM.username == "test_user_service")
    found = db_session.execute(query).scalar_one_or_none()
    log.debug(f"FOUND_SERVICE = {found}")

    assert found is not None
    assert found.username == "test_user_service"
    assert found.email == "test_user_service@gmail.com"

    # assert type(created_user) == UserResponse
