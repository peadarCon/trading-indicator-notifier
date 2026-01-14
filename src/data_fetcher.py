"""Fetch OHLCV data from Binance API."""

import requests
import pandas as pd
from datetime import datetime


BINANCE_API_URL = "https://api.binance.com/api/v3/klines"


def fetch_ohlcv(
    symbol: str = "BTCUSDT",
    interval: str = "1d",
    limit: int = 100,
) -> pd.DataFrame:
    """
    Fetch OHLCV (Open, High, Low, Close, Volume) data from Binance.

    Args:
        symbol: Trading pair symbol (e.g., "BTCUSDT")
        interval: Candle interval (e.g., "1d" for daily)
        limit: Number of candles to fetch (max 1000)

    Returns:
        DataFrame with columns: timestamp, open, high, low, close, volume
    """
    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit,
    }

    response = requests.get(BINANCE_API_URL, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    df = pd.DataFrame(data, columns=[
        "timestamp", "open", "high", "low", "close", "volume",
        "close_time", "quote_volume", "trades", "taker_buy_base",
        "taker_buy_quote", "ignore"
    ])

    # Convert to appropriate types
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)

    # Keep only relevant columns
    df = df[["timestamp", "open", "high", "low", "close", "volume"]]

    return df


def get_current_price(symbol: str = "BTCUSDT") -> float:
    """Get the current price for a symbol."""
    url = "https://api.binance.com/api/v3/ticker/price"
    response = requests.get(url, params={"symbol": symbol}, timeout=10)
    response.raise_for_status()
    return float(response.json()["price"])
