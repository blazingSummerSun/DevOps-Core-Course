import pytest

from app_python.app import app


@pytest.fixture
def client():
    """Create test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_index_endpoint_structure(client):
    """Test main endpoint returns correct structure."""
    response = client.get("/")

    assert response.status_code == 200

    data = response.get_json()

    # Top-level keys
    assert "service" in data
    assert "system" in data
    assert "runtime" in data
    assert "request" in data
    assert "endpoints" in data

    # Service structure
    assert data["service"]["name"] == "devops-info-service"
    assert "version" in data["service"]
    assert "framework" in data["service"]

    # System fields exist (not exact values!)
    assert "hostname" in data["system"]
    assert isinstance(data["system"]["cpu_count"], int)


def test_health_endpoint(client):
    """Test health endpoint returns healthy status."""
    response = client.get("/health")

    assert response.status_code == 200

    data = response.get_json()

    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert isinstance(data["uptime_seconds"], int)


def test_404_error(client):
    """Test unknown endpoint returns 404 JSON."""
    response = client.get("/unknown")

    assert response.status_code == 404

    data = response.get_json()
    assert data["error"] == "Not Found"
