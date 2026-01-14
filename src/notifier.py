"""Discord webhook notifications."""

import os
from datetime import datetime

import requests

from .confluence import ConfluenceResult
from .indicators import Signal


def send_discord_notification(
    result: ConfluenceResult,
    webhook_url: str | None = None,
    min_confluence: int = 3,
) -> bool:
    """
    Send a Discord notification about confluence signals.

    Args:
        result: ConfluenceResult from confluence analysis
        webhook_url: Discord webhook URL (or uses DISCORD_WEBHOOK_URL env var)
        min_confluence: Minimum indicators for confluence alert

    Returns:
        True if notification sent successfully
    """
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("Warning: No Discord webhook URL configured")
        return False

    # Determine embed color based on signal
    direction = result.get_confluence_direction(min_confluence)
    if direction == Signal.BULLISH:
        color = 0x00FF00  # Green
        emoji = "🟢"
        title = f"{emoji} BULLISH Confluence Detected"
    elif direction == Signal.BEARISH:
        color = 0xFF0000  # Red
        emoji = "🔴"
        title = f"{emoji} BEARISH Confluence Detected"
    else:
        color = 0xFFFF00  # Yellow
        emoji = "🟡"
        title = f"{emoji} Market Analysis Update"

    # Build indicator breakdown
    bullish_indicators = []
    bearish_indicators = []
    neutral_indicators = []

    for ind in result.indicator_results:
        line = f"**{ind.name}**: {ind.description}"
        if ind.signal == Signal.BULLISH:
            bullish_indicators.append(f"🟢 {line}")
        elif ind.signal == Signal.BEARISH:
            bearish_indicators.append(f"🔴 {line}")
        else:
            neutral_indicators.append(f"⚪ {line}")

    # Build description
    description_parts = [
        f"**Symbol**: {result.symbol}",
        f"**Price**: ${result.current_price:,.2f}",
        f"**Time**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        f"**Signal Summary**: {result.bullish_count} Bullish / {result.bearish_count} Bearish / {result.neutral_count} Neutral",
    ]

    # Build fields for each signal type
    fields = []

    if bullish_indicators:
        fields.append({
            "name": f"🟢 Bullish ({len(bullish_indicators)})",
            "value": "\n".join(bullish_indicators[:5]),  # Limit to 5
            "inline": False,
        })

    if bearish_indicators:
        fields.append({
            "name": f"🔴 Bearish ({len(bearish_indicators)})",
            "value": "\n".join(bearish_indicators[:5]),
            "inline": False,
        })

    if neutral_indicators:
        fields.append({
            "name": f"⚪ Neutral ({len(neutral_indicators)})",
            "value": "\n".join(neutral_indicators[:5]),
            "inline": False,
        })

    embed = {
        "title": title,
        "description": "\n".join(description_parts),
        "color": color,
        "fields": fields,
        "footer": {
            "text": "Trading Indicator Notifier • Not financial advice"
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

    payload = {
        "embeds": [embed],
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Failed to send Discord notification: {e}")
        return False


def send_test_notification(webhook_url: str | None = None) -> bool:
    """Send a test notification to verify webhook is working."""
    webhook_url = webhook_url or os.getenv("DISCORD_WEBHOOK_URL")

    if not webhook_url:
        print("Error: No Discord webhook URL configured")
        return False

    payload = {
        "embeds": [{
            "title": "🔔 Test Notification",
            "description": "Trading Indicator Notifier is configured correctly!",
            "color": 0x00BFFF,
            "timestamp": datetime.utcnow().isoformat(),
        }]
    }

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        print("Test notification sent successfully!")
        return True
    except requests.RequestException as e:
        print(f"Failed to send test notification: {e}")
        return False
