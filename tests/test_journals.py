from fastapi.testclient import TestClient
import uuid
from app.main import app

def test_journal_requires_auth(client):
    res = client.get("/journals")
    assert res.status_code == 401

    res = client.post("/journals", json={
        "title": "Unauthorized",
        "content": "No token here.",
        "mood": "anxious"
    })
    assert res.status_code == 401

def test_create_journal_missing_fields(client):
    register_data = {
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "testpassword"
    }
    res = client.post("/auth/register", json=register_data)
    assert res.status_code == 200

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    res = client.post("/auth/login", data=login_data)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    entry_data = {
        "content": "Missing title.",
        "mood": "sad"
    }
    res = client.post("/journals", json=entry_data, headers=headers)
    assert res.status_code == 422

def test_empty_journal_list(client):
    register_data = {
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "testpassword"
    }
    res = client.post("/auth/register", json=register_data)
    assert res.status_code == 200

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    res = client.post("/auth/login", data=login_data)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/journals", headers=headers)
    assert res.status_code == 200
    assert res.json() == []