import pytest
from fastapi.testclient import TestClient

from fastqueue.api import app
from fastqueue.database import engine, SessionLocal
from fastqueue.models import Base


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(scope="module")
def connection():
    connection = engine.connect()
    Base.metadata.create_all(bind=engine)
    yield connection
    Base.metadata.drop_all(bind=engine)
    connection.close()


@pytest.fixture(scope="function")
def session(connection):
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
