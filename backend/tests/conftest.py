from __future__ import annotations

from typing import Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient
from src.app import create_app
from src.config import TestingSettings


@pytest.fixture(scope="session")
def app() -> Flask:
    """Create and configure a Flask application instance for testing."""
    test_settings = TestingSettings()
    app = create_app(test_settings)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Provide a test client for simulating HTTP requests."""
    return app.test_client()