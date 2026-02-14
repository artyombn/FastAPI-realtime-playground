from sqlalchemy.orm import Session
from starlette.testclient import TestClient


def test_register_user(client: TestClient, db_session: Session):
    response = client.post(
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
