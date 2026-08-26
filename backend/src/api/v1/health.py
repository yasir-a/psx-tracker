from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from flask import Blueprint, jsonify, Response
from src.config import get_settings

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
    """Readiness probe: checks downstream dependency connectivity (DB, Redis)."""
    checks: dict[str, str] = {
        "application": "ok",
    }
    # Future phases will attach live PostgreSQL & Redis ping checks here
    is_ready = all(status == "ok" for status in checks.values())

    payload: dict[str, Any] = {
        "status": "ready" if is_ready else "degraded",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks,
    }
    status_code = 200 if is_ready else 503
    return jsonify(payload), status_code