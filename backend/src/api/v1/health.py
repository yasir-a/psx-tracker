from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from flask import Blueprint, current_app, jsonify, Response
from sqlalchemy import text

from src.config import get_settings
from src.infrastructure.cache.redis_client import is_redis_available
from src.infrastructure.db.session import get_engine

health_bp = Blueprint("health", __name__)
_START_TIME = datetime.now(timezone.utc)


@health_bp.route("/health", methods=["GET"])
def health_check() -> tuple[Response, int]:
    """Liveness probe: verifies that the web service is alive and serving requests."""
    settings = get_settings()
    uptime_seconds = (datetime.now(timezone.utc) - _START_TIME).total_seconds()

    payload: dict[str, Any] = {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENV,
        "uptime_seconds": round(uptime_seconds, 2),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    return jsonify(payload), 200


@health_bp.route("/ready", methods=["GET"])
def readiness_check() -> tuple[Response, int]:
    """Readiness probe: checks downstream dependency connectivity (PostgreSQL, Redis)."""
    checks: dict[str, str] = {
        "application": "ok",
    }

    # Database connectivity check
    try:
        engine = get_engine()
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as e:
        current_app.logger.warning("Database readiness check failed: %s", str(e))
        checks["database"] = "unavailable"

    # Redis connectivity check
    checks["redis"] = "ok" if is_redis_available() else "unavailable"

    # Application is ready if primary database is available
    is_ready = checks.get("application") == "ok" and checks.get("database") == "ok"
    payload: dict[str, Any] = {
        "status": "ready" if is_ready else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }
    status_code = 200 if is_ready else 503
    return jsonify(payload), status_code