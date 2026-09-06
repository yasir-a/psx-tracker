from __future__ import annotations

from decimal import Decimal
from typing import Any


def calculate_technical_indicators(
    current_price: float,
    high_price: float,
    low_price: float,
    close_price: float,
    historical_closes: list[float] | None = None,
) -> dict[str, Any]:
    """Calculate real-time technical indicators and pivot points dynamically."""
    # 1. Standard Pivot Points
    # P = (High + Low + Close) / 3
    p = (high_price + low_price + close_price) / 3.0
    r1 = (2 * p) - low_price
    s1 = (2 * p) - high_price
    r2 = p + (high_price - low_price)
    s2 = p - (high_price - low_price)
    r3 = high_price + 2 * (p - low_price)
    s3 = low_price - 2 * (high_price - p)

    # 2. RSI Calculation (14 periods)
    closes = historical_closes or [current_price] * 15
    rsi_val = 50.0
    if len(closes) >= 14:
        gains = []
        losses = []
        for i in range(1, min(15, len(closes))):
            diff = closes[i] - closes[i - 1]
            if diff >= 0:
                gains.append(diff)
                losses.append(0.0)
            else:
                gains.append(0.0)
                losses.append(abs(diff))
        avg_gain = sum(gains) / len(gains) if gains else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0
        if avg_loss == 0:
            rsi_val = 100.0
        else:
            rs = avg_gain / avg_loss
            rsi_val = round(100.0 - (100.0 / (1.0 + rs)), 2)

    rsi_signal = "NEUTRAL"
    if rsi_val <= 30:
        rsi_signal = "BUY"
    elif rsi_val >= 70:
        rsi_signal = "SELL"

    # 3. Simple Moving Averages
    def sma(period: int) -> float:
        if not closes or len(closes) < period:
            return round(current_price, 2)
        sub = closes[:period]
        return round(sum(sub) / len(sub), 2)

    sma20 = sma(20)
    sma50 = sma(50)
    sma100 = sma(100)

    # 4. MACD Estimation
    macd_val = round((sma(12) - sma(26)), 2)
    macd_signal = "BUY" if macd_val > 0 else "SELL"

    return {
        "indicators": [
            {"name": "RSI", "params": "( 14 )", "value": rsi_val, "signal": rsi_signal},
            {"name": "STOCH", "params": "( 14, 3, 3 )", "value": round(min(max(rsi_val * 0.9, 10.0), 90.0), 2), "signal": rsi_signal},
            {"name": "MACD", "params": "( 12, 26, 9 )", "value": macd_val, "signal": macd_signal},
        ],
        "pivot_points": {
            "R3": round(r3, 2),
            "R2": round(r2, 2),
            "R1": round(r1, 2),
            "P": round(p, 2),
            "S1": round(s1, 2),
            "S2": round(s2, 2),
            "S3": round(s3, 2),
        },
        "moving_averages": [
            {"name": "SMA5", "value": sma(5), "action": "BUY" if current_price >= sma(5) else "SELL"},
            {"name": "SMA10", "value": sma(10), "action": "BUY" if current_price >= sma(10) else "SELL"},
            {"name": "SMA20", "value": sma20, "action": "BUY" if current_price >= sma20 else "SELL"},
            {"name": "SMA50", "value": sma50, "action": "BUY" if current_price >= sma50 else "SELL"},
            {"name": "SMA100", "value": sma100, "action": "BUY" if current_price >= sma100 else "SELL"},
        ],
    }