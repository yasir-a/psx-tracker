from __future__ import annotations

from uuid import UUID
from flask import Blueprint, g, jsonify, request, Response

from src.api.decorators import jwt_required
from src.application.services.analytics_service import AnalyticsService
from src.infrastructure.db.session import get_db_session

analytics_bp = Blueprint("analytics", __name__, url_prefix="/analytics")


@analytics_bp.route("/summary", methods=["GET"])
@jwt_required
def get_analytics_summary() -> tuple[Response, int]:
    """Retrieve KSE-100 benchmark alpha/beta, sector concentration, and NCCPL CGT schedule."""
    portfolio_id_str = request.args.get("portfolio_id")
    pid = UUID(portfolio_id_str) if portfolio_id_str and portfolio_id_str != "consolidated" else None

    session = get_db_session()
    service = AnalyticsService(session)
    data = service.get_portfolio_analytics(pid, g.current_user_id)

    return jsonify(data), 200