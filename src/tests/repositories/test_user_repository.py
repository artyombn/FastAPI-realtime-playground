import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.core.user.entities import CreateUser as CreateUserSchema
from src.database.repositories.user import UserRepository
from src.database.models.user import UserORM

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


def test_add_user(db_session: Session):
    user = CreateUserSchema(
        username="test_user_repository",
        email="test_user_repository@gmail.com",
        password="MyCat@Barsik7",
        is_admin=False,
    )
    log.debug(f"USER_REPOSITORY = {user}")

    res = UserRepository.add(db_session, user)
    log.debug(f"RES_REPOSITORY = {res}")

    query = select(UserORM).filter(UserORM.username == "test_user_repository")
    found = db_session.execute(query).scalar_one_or_none()

    assert found is not None
    assert found.username == "test_user_repository"
    assert found.email == "test_user_repository@gmail.com"
