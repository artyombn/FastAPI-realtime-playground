from http import HTTPStatus

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.user import UserORM


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post(
        "/v1/api/users/register",
        json={
            "username": "test_user2",
            "email": "test_user2@gmail.com",
            "password": "MyCat@Barsik7",
        },
    )

    assert response.status_code == HTTPStatus.OK

    body = response.json()
    assert body["username"] == "test_user2"
    assert body["email"] == "test_user2@gmail.com"
    assert "id" in body

    stmt = select(UserORM).where(UserORM.username == "test_user2")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert body["id"] == found.id
    assert found.username == "test_user2"
    assert found.email == "test_user2@gmail.com"


@pytest.mark.asyncio
async def test_register_user_already_exists(
    client: AsyncClient, db_session: AsyncSession
):
    db_session.add(
        UserORM(
            username="test_user3",
            email="test_user3@gmail.com",
            password="MyCat@Barsik7",
        )
    )
    await db_session.commit()

    stmt = select(UserORM).where(UserORM.email == "test_user3@gmail.com")
    result = await db_session.execute(stmt)
    found = result.scalar_one_or_none()

    assert found is not None
    assert found.username == "test_user3"
    assert found.email == "test_user3@gmail.com"

    response = await client.post(
        "/v1/api/users/register",
        json={
            "username": "test_user3",
            "email": "test_user3@gmail.com",
            "password": "MyCat@Barsik7",
        },
    )

    assert response.status_code == HTTPStatus.CONFLICT
    assert response.json() == {"detail": "User already exists"}
