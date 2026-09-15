from __future__ import annotations

from uuid import UUID
from flask import Blueprint, jsonify, request, Response, g

from src.api.decorators import jwt_required
from src.application.services.dividend_analytics_service import DividendAnalyticsService
from src.infrastructure.db.session import get_db_session

dividends_bp = Blueprint("dividends", __name__, url_prefix="/dividends")


@dividends_bp.route("/analytics", methods=["GET"])
@jwt_required
def get_dividend_analytics() -> tuple[Response, int]:
    """Return dividend performance breakdown, yield on cost, and payout timelines."""
    portfolio_id_str = request.args.get("portfolio_id")
    year_str = request.args.get("year")

    portfolio_id = None
    if portfolio_id_str and portfolio_id_str != "consolidated":
        try:
            portfolio_id = UUID(portfolio_id_str)
        except ValueError:
            portfolio_id = None

    year = None
    if year_str and year_str != "all":
        try:
            year = int(year_str)
        except ValueError:
            year = None

    session = get_db_session()
    service = DividendAnalyticsService(session)
    data = service.get_dividend_analytics(
        user_id=g.current_user_id,
        portfolio_id=portfolio_id,
        year=year,
    )
    return jsonify(data), 200