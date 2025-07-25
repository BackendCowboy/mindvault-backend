# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.logger import logger
from app.main import app
from app.database import get_session  # your real dependency

# ✅ In-memory test DB engine
TEST_DATABASE_URL = "sqlite://"
test_engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)


# ✅ Reset schema before each test
@pytest.fixture(autouse=True)
def setup_and_reset_db():
    SQLModel.metadata.drop_all(test_engine)
    SQLModel.metadata.create_all(test_engine)


# ✅ Provide test session
@pytest.fixture()
def session():
    with Session(test_engine) as session:
        yield session


# ✅ Override the app’s get_session to use test session
@pytest.fixture()
def client(session):
    def override_get_session():
        yield session

    app.dependency_overrides[get_session] = override_get_session

    # 🔍 Log all routes to confirm
    logger.info("\n📦 LOADED ROUTES:")
    for r in app.routes:
        logger.info(r.path)

    return TestClient(app)
