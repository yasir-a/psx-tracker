from __future__ import annotations

from flask.testing import FlaskClient


def test_market_symbols_listing(client: FlaskClient) -> None:
    response = client.get("/api/v1/market/symbols")
    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] > 0
    symbols = [s["symbol"] for s in data["securities"]]
    assert "ENGRO" in symbols
    assert "SYS" in symbols


def test_market_single_quote(client: FlaskClient) -> None:
    response = client.get("/api/v1/market/quote/ENGRO")
    assert response.status_code == 200
    data = response.get_json()
    assert data["symbol"] == "ENGRO"
    assert data["current_price"] > 0
    assert "change_percent" in data


def test_market_bulk_quotes(client: FlaskClient) -> None:
    response = client.post(
        "/api/v1/market/quotes",
        json={"symbols": ["ENGRO", "SYS", "LUCK"]},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert "quotes" in data
    assert "ENGRO" in data["quotes"]
    assert "SYS" in data["quotes"]


def test_market_historical_quotes(client: FlaskClient) -> None:
    response = client.get("/api/v1/market/historical/ENGRO?days=7")
    assert response.status_code == 200
    data = response.get_json()
    assert data["symbol"] == "ENGRO"
    assert len(data["history"]) > 0