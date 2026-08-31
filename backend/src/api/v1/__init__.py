from __future__ import annotations

from flask import Blueprint
from src.api.v1.analytics import analytics_bp
from src.api.v1.auth import auth_bp
from src.api.v1.corporate_actions import corporate_actions_bp
from src.api.v1.health import health_bp
from src.api.v1.market import market_bp
from src.api.v1.portfolio import portfolio_bp
from src.api.v1.system import system_bp

v1_bp = Blueprint("v1", __name__, url_prefix="/api/v1")

v1_bp.register_blueprint(health_bp)
v1_bp.register_blueprint(auth_bp)
v1_bp.register_blueprint(portfolio_bp)
v1_bp.register_blueprint(market_bp)
v1_bp.register_blueprint(corporate_actions_bp)
v1_bp.register_blueprint(analytics_bp)
v1_bp.register_blueprint(system_bp)