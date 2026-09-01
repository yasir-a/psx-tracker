from __future__ import annotations

from datetime import date, timedelta
from flask import Blueprint, Response, jsonify, request

from src.infrastructure.market.detailed_market_data import get_detailed_stock_intelligence
from src.infrastructure.market.provider_factory import get_market_service

market_bp = Blueprint("market", __name__, url_prefix="/market")


@market_bp.route("/symbols", methods=["GET"])
@market_bp.route("/securities", methods=["GET"])
def list_securities() -> tuple[Response, int]:
    """Retrieve complete catalog of securities with sector classifications."""
    service = get_market_service()
    securities = service.list_all_securities()
    items = [
        {
            "symbol": s.symbol,
            "name": s.name,
            "sector": s.sector,
            "is_active": s.is_active,
        }
        for s in securities
    ]
    return jsonify({
        "securities": items,
        "count": len(items),
    }), 200


@market_bp.route("/quote/<string:symbol>", methods=["GET"])
def get_quote(symbol: str) -> tuple[Response, int]:
    """Get live market quote for a single PSX symbol."""
    service = get_market_service()
    quote = service.get_quote(symbol.upper().strip())
    if not quote:
        return jsonify({"error": {"code": "NOT_FOUND", "message": f"Quote for {symbol} not found"}}), 404

    return jsonify({
        "symbol": quote.symbol,
        "current_price": float(quote.current_price.amount),
        "previous_close": float(quote.previous_close.amount),
        "change": float(quote.change.amount),
        "change_percent": float(quote.change_percent),
        "volume": quote.volume,
        "status": quote.status.value,
        "updated_at": quote.updated_at.isoformat(),
    }), 200


@market_bp.route("/quotes", methods=["POST"])
def get_bulk_quotes() -> tuple[Response, int]:
    """Get live quotes for multiple symbols."""
    data = request.get_json(silent=True) or {}
    symbols = data.get("symbols", [])
    service = get_market_service()
    quotes = service.get_bulk_quotes(symbols)

    quotes_dict = {
        sym: {
            "symbol": q.symbol,
            "current_price": float(q.current_price.amount),
            "previous_close": float(q.previous_close.amount),
            "change": float(q.change.amount),
            "change_percent": float(q.change_percent),
            "volume": q.volume,
            "status": q.status.value,
            "updated_at": q.updated_at.isoformat(),
        }
        for sym, q in quotes.items()
    }

    return jsonify({
        "quotes": quotes_dict,
        **quotes_dict,
    }), 200

@market_bp.route("/historical/<string:symbol>", methods=["GET"])
def get_historical_quotes(symbol: str) -> tuple[Response, int]:
    """Get historical daily price bars for a symbol."""
    days = int(request.args.get("days", 30))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    service = get_market_service()
    history = service.get_historical_prices(symbol.upper().strip(), start_date=start_date, end_date=end_date)

    return jsonify({
        "symbol": symbol.upper().strip(),
        "history": [
            {
                "trade_date": h.trade_date.isoformat(),
                "open_price": float(h.open_price.amount),
                "high_price": float(h.high_price.amount),
                "low_price": float(h.low_price.amount),
                "close_price": float(h.close_price.amount),
                "volume": h.volume,
            }
            for h in history
        ],
    }), 200


@market_bp.route("/details/<string:symbol>", methods=["GET"])
def get_security_details(symbol: str) -> tuple[Response, int]:
    """Get comprehensive security intelligence for all 6 tabs (Live, Fundamentals, Technicals, Announcements, Profile, Competitors)."""
    data = get_detailed_stock_intelligence(symbol)
    return jsonify(data), 200