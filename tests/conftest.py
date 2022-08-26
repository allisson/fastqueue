import pytest
from fastapi.testclient import TestClient

from fastqueue.main import app


@pytest.fixture
def client():
    return TestClient(app)
