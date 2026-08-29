from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID
from flask import Blueprint, g, jsonify, request, Response

from src.api.decorators import jwt_required
from src.api.errors import ValidationError
from src.application.services.portfolio_accounting_service import PortfolioAccountingService
from src.domain.accounting.transaction_type import TransactionType
from src.infrastructure.db.session import get_db_session

portfolio_bp = Blueprint("portfolio", __name__, url_prefix="/portfolio")


def _get_service() -> PortfolioAccountingService:
    session = get_db_session()
    return PortfolioAccountingService(session)


@portfolio_bp.route("/mine", methods=["GET"])
@jwt_required
def list_my_portfolios() -> tuple[Response, int]:
    """Retrieve all portfolios/accounts belonging to the authenticated user."""
    service = _get_service()
    portfolios = service.get_user_portfolios(g.current_user_id)
    return jsonify({"portfolios": portfolios}), 200


@portfolio_bp.route("/create", methods=["POST"])
@jwt_required
def create_portfolio() -> tuple[Response, int]:
    """Create a new portfolio account (e.g. Darson, BMA, CDC IAS)."""
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    if not name or not name.strip():
        raise ValidationError("Portfolio name is required")

    service = _get_service()
    portfolio = service.create_portfolio(
        user_id=g.current_user_id,
        name=name,
        description=data.get("description"),
    )
    session = get_db_session()
    session.commit()
    return jsonify(portfolio), 201


@portfolio_bp.route("/consolidated-valuation", methods=["GET"])
@jwt_required
def get_consolidated_valuation() -> tuple[Response, int]:
    """Get aggregate wealth and combined stock positions across all user portfolios."""
    service = _get_service()
    valuation = service.get_consolidated_valuation(g.current_user_id)
    return jsonify(valuation), 200


@portfolio_bp.route("/<string:portfolio_id>/valuation", methods=["GET"])
@jwt_required
def get_valuation(portfolio_id: str) -> tuple[Response, int]:
    """Calculate and return real-time portfolio holdings, cash, and P&L metrics."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.verify_ownership(pid, g.current_user_id)

    valuation = service.get_portfolio_valuation(pid)
    return jsonify(valuation), 200


@portfolio_bp.route("/<string:portfolio_id>/transactions", methods=["GET"])
@jwt_required
def get_transactions(portfolio_id: str) -> tuple[Response, int]:
    """Fetch chronological transaction ledger history for a portfolio."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.verify_ownership(pid, g.current_user_id)

    history = service.get_transactions_history(pid)
    return jsonify({"transactions": history}), 200


@portfolio_bp.route("/<string:portfolio_id>/transactions", methods=["POST"])
@jwt_required
def create_transaction(portfolio_id: str) -> tuple[Response, int]:
    """Execute and record a trade or cash movement."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.verify_ownership(pid, g.current_user_id)

    data = request.get_json(silent=True) or {}
    tx_type_str = data.get("transaction_type")
    if not tx_type_str:
        raise ValidationError("Missing transaction_type")

    try:
        tx_type = TransactionType(tx_type_str.upper())
        symbol = data.get("symbol")
        qty = Decimal(str(data.get("quantity", 0)))
        price = Decimal(str(data.get("price_per_share", 0)))
        fee = Decimal(str(data.get("brokerage_fee", 0)))
        notes = data.get("notes")
        exec_at = datetime.fromisoformat(data["executed_at"]) if "executed_at" in data else None
    except Exception as e:
        raise ValidationError(f"Invalid transaction payload: {str(e)}")

    result = service.record_transaction(
        portfolio_id=pid,
        transaction_type=tx_type,
        symbol=symbol,
        quantity=qty,
        price_per_share=price,
        brokerage_fee=fee,
        executed_at=exec_at,
        notes=notes,
    )
    session = get_db_session()
    session.commit()

    return jsonify(result), 201


@portfolio_bp.route("/transfer-shares", methods=["POST"])
@jwt_required
def transfer_shares() -> tuple[Response, int]:
    """Transfer shares between accounts (e.g. Darson -> CDC IAS) preserving FIFO cost basis."""
    data = request.get_json(silent=True) or {}
    from_pid_str = data.get("from_portfolio_id")
    to_pid_str = data.get("to_portfolio_id")
    symbol = data.get("symbol")
    qty_val = data.get("quantity")

    if not from_pid_str or not to_pid_str or not symbol or qty_val is None:
        raise ValidationError("Missing required fields: from_portfolio_id, to_portfolio_id, symbol, quantity")

    try:
        from_pid = UUID(from_pid_str)
        to_pid = UUID(to_pid_str)
        qty = Decimal(str(qty_val))
        cdc_fee = Decimal(str(data.get("cdc_transfer_fee", 0)))
        notes = data.get("notes")
    except Exception as e:
        raise ValidationError(f"Invalid transfer data: {str(e)}")

    service = _get_service()
    result = service.transfer_shares_between_portfolios(
        user_id=g.current_user_id,
        from_portfolio_id=from_pid,
        to_portfolio_id=to_pid,
        symbol=symbol,
        quantity=qty,
        cdc_transfer_fee=cdc_fee,
        notes=notes,
    )
    session = get_db_session()
    session.commit()

    return jsonify(result), 200