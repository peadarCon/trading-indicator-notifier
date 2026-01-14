"""Main entry point for the trading indicator notifier."""

import argparse
import os
import time
from datetime import datetime

import schedule
from dotenv import load_dotenv

from .confluence import ConfluenceDetector
from .data_fetcher import fetch_ohlcv, get_current_price
from .indicators import Signal, get_default_indicators
from .notifier import send_discord_notification, send_test_notification


def analyze_market(
    symbol: str = "BTCUSDT",
    min_confluence: int = 3,
    always_notify: bool = False,
) -> None:
    """
    Fetch data, analyze indicators, and send notifications if confluence detected.

    Args:
        symbol: Trading pair to analyze
        min_confluence: Minimum indicators needed for confluence alert
        always_notify: If True, always send notification regardless of confluence
    """
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Analyzing {symbol}...")

    try:
        # Fetch daily candle data
        df = fetch_ohlcv(symbol=symbol, interval="1d", limit=100)
        print(f"  Fetched {len(df)} candles")

        # Run confluence analysis
        detector = ConfluenceDetector()
        result = detector.analyze(df, symbol=symbol)

        # Print summary
        print(f"  Price: ${result.current_price:,.2f}")
        print(f"  Signals: {result.bullish_count} Bullish / {result.bearish_count} Bearish / {result.neutral_count} Neutral")

        # Print individual indicator results
        for ind in result.indicator_results:
            signal_icon = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}[ind.signal.value]
            print(f"    {signal_icon} {ind.name}: {ind.description}")

        # Check for confluence
        has_confluence = result.has_confluence(min_confluence)
        direction = result.get_confluence_direction(min_confluence)

        if has_confluence:
            print(f"\n  ⚡ CONFLUENCE DETECTED: {direction.value.upper()} ({max(result.bullish_count, result.bearish_count)}/{result.total_indicators} indicators)")

        # Send notification
        if always_notify or has_confluence:
            print("  Sending Discord notification...")
            success = send_discord_notification(result, min_confluence=min_confluence)
            if success:
                print("  ✓ Notification sent!")
            else:
                print("  ✗ Failed to send notification")
        else:
            print(f"  No confluence (need {min_confluence}+ agreeing indicators)")

    except Exception as e:
        print(f"  Error during analysis: {e}")
        raise


def run_once(symbol: str = "BTCUSDT", min_confluence: int = 3, always_notify: bool = False) -> None:
    """Run analysis once and exit."""
    analyze_market(symbol=symbol, min_confluence=min_confluence, always_notify=always_notify)


def run_scheduled(
    symbol: str = "BTCUSDT",
    min_confluence: int = 3,
    interval_hours: int = 24,
) -> None:
    """Run analysis on a schedule."""
    print(f"Starting scheduled analysis for {symbol}")
    print(f"  Interval: every {interval_hours} hours")
    print(f"  Min confluence: {min_confluence} indicators")
    print("  Press Ctrl+C to stop\n")

    # Run immediately on start
    analyze_market(symbol=symbol, min_confluence=min_confluence)

    # Schedule future runs
    schedule.every(interval_hours).hours.do(
        analyze_market,
        symbol=symbol,
        min_confluence=min_confluence,
    )

    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute


def main():
    """CLI entry point."""
    load_dotenv()

    parser = argparse.ArgumentParser(
        description="Monitor crypto indicators for confluence signals"
    )
    parser.add_argument(
        "--symbol",
        default="BTCUSDT",
        help="Trading pair symbol (default: BTCUSDT)",
    )
    parser.add_argument(
        "--min-confluence",
        type=int,
        default=3,
        help="Minimum indicators for confluence alert (default: 3)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=None,
        help="Run on schedule every N hours (omit for single run)",
    )
    parser.add_argument(
        "--always-notify",
        action="store_true",
        help="Always send notification, even without confluence",
    )
    parser.add_argument(
        "--test-webhook",
        action="store_true",
        help="Send a test notification and exit",
    )

    args = parser.parse_args()

    if args.test_webhook:
        send_test_notification()
        return

    if args.interval:
        run_scheduled(
            symbol=args.symbol,
            min_confluence=args.min_confluence,
            interval_hours=args.interval,
        )
    else:
        run_once(
            symbol=args.symbol,
            min_confluence=args.min_confluence,
            always_notify=args.always_notify,
        )


if __name__ == "__main__":
    main()
