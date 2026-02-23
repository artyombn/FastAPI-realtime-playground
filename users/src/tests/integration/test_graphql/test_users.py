import pytest
from httpx import AsyncClient

from src.api.graphql.user.schemas import UserInput


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
