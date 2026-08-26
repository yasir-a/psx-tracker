from __future__ import annotations

from flask.testing import FlaskClient
from src.api.errors import AppError, NotFoundError, ValidationError


def test_custom_app_error_serialization() -> None:
    error = ValidationError("Invalid ticker symbol", details={"field": "symbol"})
    payload = error.to_dict()

    assert payload["error"]["code"] == "VALIDATION_ERROR"
    assert payload["error"]["message"] == "Invalid ticker symbol"
    assert payload["error"]["details"] == {"field": "symbol"}
    assert error.status_code == 400


def test_404_route_returns_json_error(client: FlaskClient) -> None:
    response = client.get("/api/v1/non-existent-endpoint")
    assert response.status_code == 404
    assert response.is_json
    data = response.get_json()

    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "message" in data["error"]


def test_405_method_not_allowed_returns_json_error(client: FlaskClient) -> None:
    response = client.post("/api/v1/health")
    assert response.status_code == 405
    assert response.is_json
    data = response.get_json()

    assert "error" in data
    assert data["error"]["code"] == "METHOD_NOT_ALLOWED"