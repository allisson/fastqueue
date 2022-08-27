import pytest
from fastapi.testclient import TestClient

from fastqueue.api import app


@pytest.fixture
def client():
    return TestClient(app)
