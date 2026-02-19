import logging
from http import HTTPStatus

import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.permissions import Permissions
from src.database.models.user import UserORM

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/v1/api/users/register",
        json={
            "username": "test_user1",
            "email": "test_user1@gmail.com",
            "password": "MyCat@Barsik7",
        },
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["username"] == "test_user1"
    assert body["email"] == "test_user1@gmail.com"
    assert "id" in body

    stmt = select(UserORM).where(UserORM.username == "test_user1")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert body["id"] == found.id
    assert found.username == "test_user1"
    assert found.email == "test_user1@gmail.com"


@pytest.mark.asyncio
async def test_register_user_already_exists(
    client: AsyncClient, db_session: AsyncSession
):
    db_session.add(
        UserORM(
            username="test_user2",
            email="test_user2@gmail.com",
            password="MyCat@Barsik7",
        )
    )
    await db_session.commit()

    stmt = select(UserORM).where(UserORM.email == "test_user2@gmail.com")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.username == "test_user2"
    assert found.email == "test_user2@gmail.com"

    response = await client.post(
        "/v1/api/users/register",
        json={
            "username": "test_user2",
            "email": "test_user2@gmail.com",
            "password": "MyCat@Barsik7",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "User already exists"}


@pytest.mark.asyncio
async def test_user_login(client: AsyncClient, db_session: AsyncSession):
    password = "MyCat@Barsik7"

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    db_session.add(
        UserORM(
            username="test_user3",
            email="test_user3@gmail.com",
            password=hashed_password,
        )
    )
    await db_session.commit()

    stmt = select(UserORM).where(UserORM.username == "test_user3")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    log.debug(f"USER_FOUND = {found.__dict__}")

    response = await client.post(
        "/v1/api/users/login",
        json={
            "username": "test_user3",
            "password": "MyCat@Barsik7",
        },
    )

    assert response.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_user_login_failed(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/v1/api/users/login",
        json={
            "username": "test_user3",
            "password": "MyCat@",
        },
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Incorrect username or password"}


@pytest.mark.asyncio
async def test_get_users_and_products(client: AsyncClient, db_session: AsyncSession):
    password = "MyCat@Barsik7"

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    db_session.add(
        UserORM(
            username="test_user4",
            email="test_user4@gmail.com",
            password=hashed_password,
            is_admin=True,
            permissions=[
                Permissions.VIEW_PRODUCT,
                Permissions.ADD_PRODUCT,
                Permissions.UPDATE_PRODUCT,
                Permissions.DELETE_PRODUCT,
            ],
        )
    )
    await db_session.commit()

    login_response = await client.post(
        "/v1/api/users/login",
        json={
            "username": "test_user4",
            "password": "MyCat@Barsik7",
        },
    )

    access_token = login_response.json()["access_token"]
    log.debug(f"ACCESS_TOKEN = {access_token}")

    response_get_users = await client.get(
        "/v1/api/users/",
        headers={"Authorization": access_token},
    )
    log.debug(f"RESPONSE_GET_USERS = {response_get_users.json()}")

    response_get_products = await client.get(
        "/v1/api/products/",
        headers={"Authorization": access_token},
    )
    log.debug(f"RESPONSE_GET_PRODUCTS = {response_get_products.json()}")

    assert response_get_users.status_code == HTTPStatus.OK
    assert response_get_products.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_users_permission_denied(
    client: AsyncClient, db_session: AsyncSession
):
    password = "MyCat@Barsik7"

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    db_session.add(
        UserORM(
            username="test_user5",
            email="test_user5@gmail.com",
            password=hashed_password,
            is_admin=False,
            permissions=[
                Permissions.VIEW_PRODUCT,
            ],
        )
    )
    await db_session.commit()

    login_response = await client.post(
        "/v1/api/users/login",
        json={
            "username": "test_user5",
            "password": "MyCat@Barsik7",
        },
    )

    access_token = login_response.json()["access_token"]

    response_get_users = await client.get(
        "/v1/api/users/",
        headers={"Authorization": access_token},
    )
    log.debug(f"RESPONSE_GET_USERS = {response_get_users.json()}")

    response_get_products = await client.get(
        "/v1/api/products/",
        headers={"Authorization": access_token},
    )

    assert response_get_users.status_code == HTTPStatus.FORBIDDEN
    assert response_get_products.status_code == HTTPStatus.OK


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, db_session: AsyncSession):
    password = "MyCat@Barsik7"

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    db_session.add(
        UserORM(
            username="test_user6",
            email="test_user6@gmail.com",
            password=hashed_password,
            is_admin=False,
            permissions=[
                Permissions.VIEW_PRODUCT,
            ],
        )
    )
    await db_session.commit()

    login_response = await client.post(
        "/v1/api/users/login",
        json={
            "username": "test_user6",
            "password": "MyCat@Barsik7",
        },
    )

    access_token = login_response.json()["access_token"]

    response_get_me = await client.get(
        "/v1/api/users/me",
        headers={"Authorization": access_token},
    )

    assert response_get_me.status_code == HTTPStatus.OK
    assert response_get_me.json()["id"] == login_response.json()["user"]["id"]
    assert response_get_me.json()["username"] == "test_user6"
    assert response_get_me.json()["email"] == "test_user6@gmail.com"
