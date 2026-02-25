import logging

import bcrypt
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from users.database.models.user import UserORM
from users.api.graphql.user.schemas import UserInput

logger = logging.getLogger("fastapi-app")


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    user = UserInput(username="olga", email="olga@gmail.com", password="MyCat@Barsik7")

    query = """
    mutation RegisterUser($user: UserInput!) {
        register(user: $user) {
            username
            email
        }
    }
    """
    variables = {
        "user": {
            "username": user.username,
            "email": user.email,
            "password": user.password,
        }
    }

    # БЕЗ VARIABLES
    # query = """
    # mutation {
    #     register(
    #         user: {
    #             username: "olga"
    #             email: "olga@gmail.com"
    #             password: "MyCat@Barsik7"
    #         }
    #     ) {
    #         username
    #         email
    #     }
    # }

    response = await client.post(
        "/v1/graphql", json={"query": query, "variables": variables}
    )

    data = response.json()

    assert response.status_code == 200
    assert "data" in data
    assert data["data"]["register"]["username"] == "olga"
    assert data["data"]["register"]["email"] == "olga@gmail.com"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession):
    password = "MyCat@Barsik7"

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )

    db_session.add(
        UserORM(
            username="graphql_user1",
            email="graphql_user1@gmail.com",
            password=hashed_password,
        )
    )
    await db_session.commit()

    query = """
    mutation LoginUser {
        login(username: "graphql_user1", password: "MyCat@Barsik7") {
            accessToken
            refreshToken
        }
    }
    """
    response = await client.post("/v1/graphql", json={"query": query})
    assert response.status_code == 200

    data = response.json()
    assert "data" in data
    assert "accessToken" in data["data"]["login"]
    assert "refreshToken" in data["data"]["login"]


@pytest.mark.asyncio
async def test_login_fail(client: AsyncClient):
    query = """
    mutation {
        login(username: "graphql_user1", password: "MyCat@Barsik777") {
            accessToken
            refreshToken
        }
    }
    """
    response = await client.post("/v1/graphql", json={"query": query})

    data = response.json()
    logger.debug(f"DATA = {data}")
    assert response.status_code == 200

    assert "errors" in data
    assert "Incorrect username or password" in data["errors"][0]["message"]
