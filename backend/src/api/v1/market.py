from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any
from flask import Blueprint, jsonify, request, Response

from src.api.errors import NotFoundError, ValidationError
from src.infrastructure.db.repositories.pg_security_repository import PgSecurityRepository
from src.infrastructure.db.session import get_db_session
from src.infrastructure.market.provider_factory import get_market_provider, get_market_service

market_bp = Blueprint("market", __name__, url_prefix="/market")


@market_bp.route("/symbols", methods=["GET"])
def get_symbols() -> tuple[Response, int]:
    """Search and list PSX listed securities."""
    query = request.args.get("query")
    sector = request.args.get("sector")
    limit = int(request.args.get("limit", 50))

    session = get_db_session()
    repo = PgSecurityRepository(session)
    securities = repo.search(query=query, sector=sector, limit=limit)

    # Fallback to provider default catalog if database catalog is empty
    if not securities:
        provider = get_market_provider()
        securities = provider.list_all_securities()
        # Seed DB catalog
        repo.save_bulk(securities)
        session.commit()

    payload = {
        "count": len(securities),
        "securities": [
            {
                "symbol": s.symbol,
                "name": s.name,
                "sector": s.sector,
                "security_type": s.security_type.value,
                "is_active": s.is_active,
            }
            for s in securities
        ],
    }
    return jsonify(payload), 200


@market_bp.route("/quote/<string:symbol>", methods=["GET"])
def get_quote(symbol: str) -> tuple[Response, int]:
    """Fetch real-time / intraday price quote for a single symbol."""
    market_service = get_market_service()
    quote = market_service.get_quote(symbol)
    if not quote:
        raise NotFoundError(f"Security '{symbol}' not found or quote unavailable")

    payload = {
        "symbol": quote.symbol,
        "current_price": float(quote.current_price.amount),
        "previous_close": float(quote.previous_close.amount),
        "change": float(quote.change.amount),
        "change_percent": float(quote.change_percent),
        "volume": quote.volume,
        "updated_at": quote.updated_at.isoformat(),
    }
    return jsonify(payload), 200


@market_bp.route("/quotes", methods=["POST"])
def get_bulk_quotes() -> tuple[Response, int]:
    """Fetch real-time price quotes for multiple symbols."""
    data = request.get_json(silent=True) or {}
    symbols = data.get("symbols", [])
    if not isinstance(symbols, list) or not symbols:
        raise ValidationError("Field 'symbols' must be a non-empty array of symbol strings")

    market_service = get_market_service()
    quotes = market_service.get_bulk_quotes(symbols)

    payload = {
        "quotes": {
            sym: {
                "symbol": q.symbol,
                "current_price": float(q.current_price.amount),
                "previous_close": float(q.previous_close.amount),
                "change": float(q.change.amount),
                "change_percent": float(q.change_percent),
                "volume": q.volume,
                "updated_at": q.updated_at.isoformat(),
            }
            for sym, q in quotes.items()
        }
    }
    return jsonify(payload), 200


@market_bp.route("/historical/<string:symbol>", methods=["GET"])
def get_historical(symbol: str) -> tuple[Response, int]:
    """Fetch daily historical price bars for a symbol."""
    days = int(request.args.get("days", 30))
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)

    provider = get_market_provider()
    bars = provider.get_historical_prices(symbol, start_date, end_date)

    payload = {
        "symbol": symbol.upper().strip(),
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "history": [
            {
                "date": b.trade_date.isoformat(),
                "open": float(b.open_price.amount),
                "high": float(b.high_price.amount),
                "low": float(b.low_price.amount),
                "close": float(b.close_price.amount),
                "volume": b.volume,
            }
            for b in bars
        ],
    }
    return jsonify(payload), 200