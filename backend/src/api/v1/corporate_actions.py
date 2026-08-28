from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID
from flask import Blueprint, jsonify, request, Response

from src.api.decorators import jwt_required
from src.api.errors import ValidationError
from src.application.services.corporate_action_service import CorporateActionService
from src.domain.corporate_actions.tax_status import TaxStatus
from src.domain.values.money import Money
from src.infrastructure.db.session import get_db_session

corporate_actions_bp = Blueprint("corporate_actions", __name__, url_prefix="/corporate-actions")


@corporate_actions_bp.route("/dividend", methods=["POST"])
@jwt_required
def post_dividend() -> tuple[Response, int]:
    """Record a cash dividend with user-selected withholding tax (15% Filer / 30% Non-Filer)."""
    data = request.get_json(silent=True) or {}
    portfolio_id_str = data.get("portfolio_id")
    symbol = data.get("symbol")
    dps_val = data.get("dividend_per_share")
    tax_status_str = data.get("tax_status", "FILER")
    custom_wht = data.get("custom_tax_rate")
    zakat_val = data.get("zakat_deducted", 0.0)

    if not portfolio_id_str or not symbol or dps_val is None:
        raise ValidationError("Missing required fields: portfolio_id, symbol, dividend_per_share")

    try:
        portfolio_id = UUID(portfolio_id_str)
        tax_status = TaxStatus(tax_status_str.upper())
        dps = Money(Decimal(str(dps_val)), "PKR")
        zakat = Money(Decimal(str(zakat_val)), "PKR") if zakat_val else None
        custom_rate = Decimal(str(custom_wht)) if custom_wht is not None else None
    except Exception as e:
        raise ValidationError(f"Invalid input data: {str(e)}")

    session = get_db_session()
    service = CorporateActionService(session)
    result = service.apply_cash_dividend(
        portfolio_id=portfolio_id,
        symbol=symbol,
        dividend_per_share=dps,
        tax_status=tax_status,
        custom_wht_rate=custom_rate,
        zakat_deducted=zakat,
    )
    session.commit()

    return jsonify(result), 201


@corporate_actions_bp.route("/bonus", methods=["POST"])
@jwt_required
def post_bonus() -> tuple[Response, int]:
    """Record a bonus shares issuance."""
    data = request.get_json(silent=True) or {}
    portfolio_id_str = data.get("portfolio_id")
    symbol = data.get("symbol")
    bonus_ratio_val = data.get("bonus_ratio")

    if not portfolio_id_str or not symbol or bonus_ratio_val is None:
        raise ValidationError("Missing required fields: portfolio_id, symbol, bonus_ratio")

    try:
        portfolio_id = UUID(portfolio_id_str)
        bonus_ratio = Decimal(str(bonus_ratio_val))
    except Exception as e:
        raise ValidationError(f"Invalid input data: {str(e)}")

    session = get_db_session()
    service = CorporateActionService(session)
    result = service.apply_bonus_shares(
        portfolio_id=portfolio_id,
        symbol=symbol,
        bonus_ratio=bonus_ratio,
    )
    session.commit()

    return jsonify(result), 201


@corporate_actions_bp.route("/tax-report/<string:portfolio_id>", methods=["GET"])
@jwt_required
def get_tax_report(portfolio_id: str) -> tuple[Response, int]:
    """Fetch annual dividend tax report under FBR Section 150."""
    try:
        pid = UUID(portfolio_id)
        tax_year = int(request.args.get("tax_year", datetime.now(timezone.utc).year))
    except Exception as e:
        raise ValidationError(f"Invalid parameters: {str(e)}")

    session = get_db_session()
    service = CorporateActionService(session)
    report = service.get_tax_report(pid, tax_year)

    return jsonify(report), 200