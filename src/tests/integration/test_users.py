import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/v1/users/register",
        json={
            "username": "test_user2",
            "password": "MyCat@Barsik7",
            "email": "test_user2@gmail.com",
        },
    )

    assert response.status_code == 404

    # body = response.json()
    # assert body["username"] == "test_user2"
    # assert body["email"] == "test_user2@gmail.com"
    # assert "id" in body
