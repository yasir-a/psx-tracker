from __future__ import annotations

from flask.testing import FlaskClient


def test_health_endpoint_returns_200(client: FlaskClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()

    assert data["status"] == "ok"
    assert data["service"] == "PSX Portfolio Tracker"
    assert "version" in data
    assert "uptime_seconds" in data
    assert "timestamp" in data


def test_ready_endpoint_returns_200(client: FlaskClient) -> None:
    response = client.get("/api/v1/ready")
    assert response.status_code == 200
    assert response.is_json
    data = response.get_json()

    assert data["status"] == "ready"
    assert "checks" in data
    assert data["checks"]["application"] == "ok"


def test_request_id_header_attached(client: FlaskClient) -> None:
    response = client.get("/api/v1/health")
    assert "X-Request-ID" in response.headers
    assert len(response.headers["X-Request-ID"]) > 0

    custom_id = "test-request-id-12345"
    response_custom = client.get("/api/v1/health", headers={"X-Request-ID": custom_id})
    assert response_custom.headers["X-Request-ID"] == custom_id
    