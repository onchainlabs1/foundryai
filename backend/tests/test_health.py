from fastapi.testclient import TestClient

from app.main import app
from tests.conftest import create_test_system

client = TestClient(app)


def test_health():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

