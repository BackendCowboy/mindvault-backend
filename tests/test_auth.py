import uuid


def test_register_and_login(client):
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
    register_data = {"email": unique_email, "password": "testpassword"}

    res = client.post("/auth/register", json=register_data)
    assert res.status_code == 200
    user = res.json()
    assert user["email"] == register_data["email"]

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"],
    }
    res = client.post("/auth/login", data=login_data)
    assert res.status_code == 200
    assert "access_token" in res.json()
