from fastapi.testclient import TestClient
from app.main import app
import uuid

def test_user_flow(client):
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
    register_data = {
        "email": unique_email,
        "password": "testpassword"
    }

    # 1. Register user
    res = client.post("/register", json=register_data)
    assert res.status_code == 200
    user = res.json()
    assert user["email"] == register_data["email"]

    # 2. Login
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    res = client.post("/login", data=login_data)
    assert res.status_code == 200
    token = res.json()["access_token"]

    # 3. Create journal
    headers = {"Authorization": f"Bearer {token}"}
    entry_data = {
        "title": "Test Entry",
        "content": "This is a test journal entry.",
        "mood": "calm"
    }
    res = client.post("/journals", json=entry_data, headers=headers)
    assert res.status_code == 200
    entry = res.json()["entry"]
    assert entry["title"] == "Test Entry"
    assert entry["mood"] == "calm"

    # 4. Fetch journals
    res = client.get("/journals", headers=headers)
    assert res.status_code == 200
    entries = res.json()
    assert any(e["title"] == "Test Entry" for e in entries)

def test_journal_requires_auth(client):
    # Attempt to access journal routes without token
    res = client.get("/journals")
    assert res.status_code == 401

    res = client.post("/journals", json={
        "title": "Unauthorized",
        "content": "No token here.",
        "mood": "anxious"
    })
    assert res.status_code == 401

    #This test checks FastAPI's input validation
# It should reject journal entries missing required fields (e.g., title)

def test_create_journal_missing_fields(client):
    # Register & login
    register_data = {
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "testpassword"
    }
    res = client.post("/register", json=register_data)
    assert res.status_code == 200

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    res = client.post("/login", data=login_data)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Missing title field
    entry_data = {
        "content": "Missing title.",
        "mood": "sad"
    }
    res = client.post("/journals", json=entry_data, headers=headers)
    assert res.status_code == 422  # Unprocessable Entity

    # 🧼 This test ensures a new user sees an empty journal list by default
def test_empty_journal_list(client):
    # Register & login
    register_data = {
        "email": f"testuser_{uuid.uuid4().hex[:6]}@example.com",
        "password": "testpassword"
    }
    res = client.post("/register", json=register_data)
    assert res.status_code == 200

    login_data = {
        "username": register_data["email"],
        "password": register_data["password"]
    }
    res = client.post("/login", data=login_data)
    token = res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Jounals should be empty on first login initially
    res = client.get("/journals", headers=headers)
    assert res.status_code == 200
    assert res.json() == []