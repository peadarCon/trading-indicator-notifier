# Trading Indicator Notifier

Monitor crypto charts for indicator confluence and receive Discord notifications when multiple indicators align.

## Features

- Fetches daily OHLCV data from Binance
- Analyzes 7 technical indicators simultaneously
- Detects confluence (multiple indicators agreeing on direction)
- Sends Discord notifications when confluence is detected

## Indicators

| Indicator | Bullish Signal | Bearish Signal |
|-----------|----------------|----------------|
| RSI | < 30 (oversold) | > 70 (overbought) |
| MACD | Above signal line | Below signal line |
| EMA Crossover (9/21) | Fast > Slow | Fast < Slow |
| Bollinger Bands | Near lower band | Near upper band |
| Stochastic | < 20 (oversold) | > 80 (overbought) |
| ADX | Strong uptrend | Strong downtrend |
| Volume | High volume on up move | High volume on down move |

## Installation

```bash
# Clone the repo
git clone https://github.com/peadarCon/trading-indicator-notifier.git
cd trading-indicator-notifier

# Create virtual environment and install
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Discord webhook URL to `.env`:
   ```
   DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
   ```

   To get a webhook URL: Discord channel settings → Integrations → Webhooks → New Webhook → Copy URL

## Usage

```bash
# Activate virtual environment
source .venv/bin/activate

# Run single analysis
python -m src.main

# Run every 24 hours
python -m src.main --interval 24

# Analyze a different pair
python -m src.main --symbol ETHUSDT

# Change confluence threshold (default: 3)
python -m src.main --min-confluence 4

# Always notify (even without confluence)
python -m src.main --always-notify

# Test Discord webhook
python -m src.main --test-webhook
```

## Example Output

```
[2024-01-14 20:51:57] Analyzing BTCUSDT...
  Fetched 100 candles
  Price: $97,420.78
  Signals: 4 Bullish / 2 Bearish / 1 Neutral
    🟢 MACD: MACD above signal line (histogram: 662.04)
    🟢 EMA Crossover: EMA9 above EMA21 (uptrend)
    🟢 ADX: Strong uptrend (ADX:30.0, +DI:33.5 > -DI:9.1)
    🟢 Volume: High volume on up move (1.6x average)
    🔴 RSI: RSI at 70.9 (overbought > 70)
    🔴 Bollinger Bands: Price at upper Bollinger Band
    ⚪ Stochastic: Stochastic neutral (K:95.1, D:79.8)

  ⚡ CONFLUENCE DETECTED: BULLISH (4/7 indicators)
```

## Disclaimer

This tool is for educational purposes only. Not financial advice. Always do your own research before trading.
