from __future__ import annotations

from typing import Generator
import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.app import create_app
from src.config import TestingSettings
from src.infrastructure.db.base import Base
import src.infrastructure.db.models  # noqa: F401


@pytest.fixture(scope="session")
def test_settings() -> TestingSettings:
    """Provide testing settings."""
    # Use SQLite in-memory for unit and fast integration tests
    settings = TestingSettings()
    settings.DATABASE_URL = "sqlite:///:memory:"
    return settings


@pytest.fixture(scope="session")
def db_engine(test_settings: TestingSettings):
    """Create a shared database engine for testing."""
    engine = create_engine(test_settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    """Provide a transactional database session rolled back after every test."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def app(test_settings: TestingSettings) -> Flask:
    """Create and configure a Flask application instance for testing."""
    app = create_app(test_settings)
    return app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Provide a test client for simulating HTTP requests."""
    return app.test_client()