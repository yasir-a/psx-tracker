from __future__ import annotations

from flask import Blueprint
from src.api.v1.auth import auth_bp
from src.api.v1.health import health_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/api/v1")

# Register feature sub-blueprints
v1_bp.register_blueprint(health_bp)
v1_bp.register_blueprint(auth_bp)