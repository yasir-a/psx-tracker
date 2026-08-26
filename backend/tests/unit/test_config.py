from __future__ import annotations

import os
from unittest.mock import patch
from src.config import DevelopmentSettings, ProductionSettings, TestingSettings, get_settings


def test_development_settings_defaults() -> None:
    settings = DevelopmentSettings()
    assert settings.ENV == "development"
    assert settings.DEBUG is True
    assert settings.API_PREFIX == "/api/v1"


def test_testing_settings_defaults() -> None:
    settings = TestingSettings()
    assert settings.ENV == "testing"
    assert settings.DEBUG is True
    assert "test" in settings.DATABASE_URL


def test_production_settings_defaults() -> None:
    settings = ProductionSettings()
    assert settings.ENV == "production"
    assert settings.DEBUG is False


def test_get_settings_env_resolution() -> None:
    get_settings.cache_clear()
    with patch.dict(os.environ, {"FLASK_ENV": "testing"}):
        settings = get_settings()
        assert settings.ENV == "testing"
    get_settings.cache_clear()
    