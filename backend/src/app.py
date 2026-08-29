from __future__ import annotations

import logging
from flask import Flask
from src.api.errors import register_error_handlers
from src.api.middleware import register_middleware
from src.api.v1 import v1_bp
from src.config import Settings, get_settings
from src.infrastructure.db.base import Base
import src.infrastructure.db.models  # noqa: F401
from src.infrastructure.db.session import get_engine, init_db


def create_app(settings: Settings | None = None) -> Flask:
    """Application factory for PSX Portfolio Tracker backend."""
    app = Flask(__name__)

    # Load configuration
    app_settings = settings or get_settings()
    app.config.from_object(app_settings)
    app.config["SETTINGS"] = app_settings

    # Configure structured logging
    logging.basicConfig(
        level=logging.DEBUG if app_settings.DEBUG else logging.INFO,
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s",
    )

    # Initialize Database & Teardown
    init_db(app, app_settings)

    # Register Middlewares & Error Handlers
    register_middleware(app)
    register_error_handlers(app)

    # Register API Blueprints
    app.register_blueprint(v1_bp)

    return app