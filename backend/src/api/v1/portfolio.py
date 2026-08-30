from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from flask import Blueprint, Response, g, jsonify, request

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


@portfolio_bp.route("/<string:portfolio_id>", methods=["DELETE"])
@jwt_required
def delete_portfolio(portfolio_id: str) -> tuple[Response, int]:
    """Delete a portfolio account if it contains no securities."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.delete_portfolio(pid, g.current_user_id)
    session = get_db_session()
    session.commit()
    return jsonify({"message": "Account deleted successfully"}), 200


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
def list_transactions(portfolio_id: str) -> tuple[Response, int]:
    """Get chronologically ordered list of all transaction records for a portfolio."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.verify_ownership(pid, g.current_user_id)
    txs = service.get_portfolio_transactions(pid)
    return jsonify({"transactions": txs}), 200

@portfolio_bp.route("/<string:portfolio_id>/transactions", methods=["POST"])
@jwt_required
def record_transaction(portfolio_id: str) -> tuple[Response, int]:
    """Record a trade, cash deposit, or fee event."""
    pid = UUID(portfolio_id)
    service = _get_service()
    service.verify_ownership(pid, g.current_user_id)

    data = request.get_json(silent=True) or {}
    tx_type_str = data.get("transaction_type")
    if not tx_type_str:
        raise ValidationError("Missing transaction_type")

    try:
        tx_type = TransactionType(tx_type_str)
    except ValueError:
        raise ValidationError(f"Invalid transaction_type: {tx_type_str}")

    exec_at = None
    if data.get("executed_at"):
        try:
            exec_at = datetime.fromisoformat(data["executed_at"].replace("Z", "+00:00"))
        except Exception:
            exec_at = None

    tx = service.record_transaction(
        portfolio_id=pid,
        transaction_type=tx_type,
        symbol=data.get("symbol"),
        quantity=Decimal(str(data.get("quantity", 0))),
        price_per_share=Decimal(str(data.get("price_per_share", 0))),
        brokerage_fee=Decimal(str(data.get("brokerage_fee", 0))),
        regulatory_fee=Decimal(str(data.get("regulatory_fee", 0))),
        executed_at=exec_at,
        notes=data.get("notes"),
    )
    session = get_db_session()
    session.commit()
    return jsonify(tx), 201

@portfolio_bp.route("/<string:portfolio_id>/transactions/<string:transaction_id>", methods=["PUT"])
@jwt_required
def update_transaction(portfolio_id: str, transaction_id: str) -> tuple[Response, int]:
    """Edit an existing transaction and recalculate lots."""
    pid = UUID(portfolio_id)
    txid = UUID(transaction_id)
    data = request.get_json(silent=True) or {}

    service = _get_service()
    updated = service.update_transaction(
        portfolio_id=pid,
        transaction_id=txid,
        user_id=g.current_user_id,
        symbol=data.get("symbol"),
        quantity=Decimal(str(data.get("quantity", 0))),
        price_per_share=Decimal(str(data.get("price_per_share", 0))),
        brokerage_fee=Decimal(str(data.get("brokerage_fee", 0))),
        notes=data.get("notes"),
    )
    session = get_db_session()
    session.commit()
    return jsonify(updated), 200

@portfolio_bp.route("/<string:portfolio_id>/transactions/<string:transaction_id>", methods=["DELETE"])
@jwt_required
def delete_transaction(portfolio_id: str, transaction_id: str) -> tuple[Response, int]:
    """Delete a transaction and recalculate lots."""
    pid = UUID(portfolio_id)
    txid = UUID(transaction_id)
    service = _get_service()
    service.delete_transaction(pid, txid, g.current_user_id)
    session = get_db_session()
    session.commit()
    return jsonify({"message": "Transaction deleted successfully"}), 200

@portfolio_bp.route("/transfer-shares", methods=["POST"])
@jwt_required
def transfer_shares() -> tuple[Response, int]:
    """Transfer shares between user accounts (e.g. Darson -> CDC IAS) with preserved FIFO cost basis."""
    data = request.get_json(silent=True) or {}
    from_pid = data.get("from_portfolio_id")
    to_pid = data.get("to_portfolio_id")
    symbol = data.get("symbol")
    quantity = data.get("quantity")

    if not from_pid or not to_pid or not symbol or not quantity:
        raise ValidationError("Missing required fields: from_portfolio_id, to_portfolio_id, symbol, quantity")

    service = _get_service()
    res = service.transfer_shares_between_portfolios(
        user_id=g.current_user_id,
        from_portfolio_id=UUID(from_pid),
        to_portfolio_id=UUID(to_pid),
        symbol=symbol,
        quantity=Decimal(str(quantity)),
        cdc_transfer_fee=Decimal(str(data.get("cdc_transfer_fee", 0))),
        notes=data.get("notes"),
    )
    session = get_db_session()
    session.commit()
    return jsonify(res), 200