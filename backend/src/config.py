from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Environment
    ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "default-insecure-secret-key-change-in-production"

    # API Settings
    API_PREFIX: str = "/api/v1"
    APP_NAME: str = "PSX Portfolio Tracker"
    APP_VERSION: str = "0.1.0"

    # Database Settings
    DATABASE_URL: str = "postgresql://psx_user:psx_password@localhost:5432/psx_portfolio"

    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


class DevelopmentSettings(Settings):
    ENV: Literal["development", "testing", "production"] = "development"
    DEBUG: bool = True


class TestingSettings(Settings):
    ENV: Literal["development", "testing", "production"] = "testing"
    DEBUG: bool = True
    DATABASE_URL: str = "postgresql://psx_user:psx_password@localhost:5432/psx_portfolio_test"
    REDIS_URL: str = "redis://localhost:6379/1"


class ProductionSettings(Settings):
    ENV: Literal["development", "testing", "production"] = "production"
    DEBUG: bool = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Retrieve and cache settings based on FLASK_ENV or APP_ENV."""
    env = os.getenv("FLASK_ENV", os.getenv("APP_ENV", "development")).lower()
    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    return DevelopmentSettings()