from __future__ import annotations

import json
from flask.testing import FlaskClient


def test_full_portfolio_trade_lifecycle_and_valuation(client: FlaskClient) -> None:
    # 1. Register User
    reg_res = client.post(
        "/api/v1/auth/register",
        data=json.dumps({
            "email": "investor@example.com",
            "password": "Password123!",
            "full_name": "Test Investor",
        }),
        content_type="application/json",
    )
    assert reg_res.status_code == 201
    auth_token = reg_res.json["tokens"]["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 2. Create Initial Broker Account
    create_res = client.post(
        "/api/v1/portfolio/create",
        headers=headers,
        data=json.dumps({"name": "Primary Broker Account"}),
        content_type="application/json",
    )
    assert create_res.status_code == 201
    portfolio_id = create_res.json["id"]

    # 3. Deposit PKR 500,000 Cash
    dep_res = client.post(
        f"/api/v1/portfolio/{portfolio_id}/transactions",
        headers=headers,
        data=json.dumps({
            "transaction_type": "CASH_DEPOSIT",
            "price_per_share": 500000,
        }),
        content_type="application/json",
    )
    assert dep_res.status_code == 201

    # 4. BUY 500 Shares of ENGRO @ 300 PKR
    buy_res = client.post(
        f"/api/v1/portfolio/{portfolio_id}/transactions",
        headers=headers,
        data=json.dumps({
            "transaction_type": "BUY",
            "symbol": "ENGRO",
            "quantity": 500,
            "price_per_share": 300,
            "brokerage_fee": 150,
        }),
        content_type="application/json",
    )
    assert buy_res.status_code == 201

    # 5. Fetch Valuation & FIFO Lots
    val_res = client.get(f"/api/v1/portfolio/{portfolio_id}/valuation", headers=headers)
    assert val_res.status_code == 200
    val_data = val_res.json
    assert val_data["summary"]["cash_balance"] == 500000 - 150150
    assert len(val_data["holdings"]) == 1
    engro = val_data["holdings"][0]
    assert engro["symbol"] == "ENGRO"
    assert engro["quantity"] == 500
    assert len(engro["open_lots"]) == 1

    # 6. SELL 200 Shares of ENGRO @ 350 PKR
    sell_res = client.post(
        f"/api/v1/portfolio/{portfolio_id}/transactions",
        headers=headers,
        data=json.dumps({
            "transaction_type": "SELL",
            "symbol": "ENGRO",
            "quantity": 200,
            "price_per_share": 350,
            "brokerage_fee": 100,
        }),
        content_type="application/json",
    )
    assert sell_res.status_code == 201

    # 7. Check Valuation After Sell
    val_after_sell = client.get(f"/api/v1/portfolio/{portfolio_id}/valuation", headers=headers).json
    engro_after = val_after_sell["holdings"][0]
    assert engro_after["quantity"] == 300
    assert val_after_sell["summary"]["realized_gain"] > 0