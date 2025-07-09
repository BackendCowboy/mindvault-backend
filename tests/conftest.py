import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.main import app
from app.database import get_session, create_db_and_tables

# 🧪 Create fresh in-memory test DB
TEST_DATABASE_URL = "sqlite://"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})

# ✅ Run once before all tests
@pytest.fixture(scope="session", autouse=True)
def setup_db():
    SQLModel.metadata.create_all(engine)
    create_db_and_tables()  # 🔥 Add this line to build schema

# ✅ Reset tables before each test function (optional, keeps it clean)
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
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session
    return TestClient(app)