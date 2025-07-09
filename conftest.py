import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from main import app
from database import get_session

# 🧪 Create fresh in-memory test DB
TEST_DATABASE_URL = "sqlite://"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# ✅ Reset tables before each test session
@pytest.fixture(scope="function", autouse=True)
def reset_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)

@pytest.fixture()
def session():
    with Session(engine) as session:
        yield session

@pytest.fixture()
def client(session):
    # Override FastAPI's dependency with test session
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)