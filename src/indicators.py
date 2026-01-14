"""Technical indicators and signal generation."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

import pandas as pd
import ta


class Signal(Enum):
    """Trading signal direction."""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class IndicatorResult:
    """Result from an indicator analysis."""
    name: str
    signal: Signal
    value: float
    description: str


class Indicator(Protocol):
    """Protocol for indicator implementations."""
    name: str

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        """Analyze price data and return a signal."""
        ...


class RSIIndicator:
    """Relative Strength Index indicator."""

    name = "RSI"

    def __init__(self, period: int = 14, oversold: float = 30, overbought: float = 70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        rsi = ta.momentum.RSIIndicator(df["close"], window=self.period)
        current_rsi = rsi.rsi().iloc[-1]

        if current_rsi < self.oversold:
            signal = Signal.BULLISH  # Oversold = potential bounce
            desc = f"RSI at {current_rsi:.1f} (oversold < {self.oversold})"
        elif current_rsi > self.overbought:
            signal = Signal.BEARISH  # Overbought = potential drop
            desc = f"RSI at {current_rsi:.1f} (overbought > {self.overbought})"
        else:
            signal = Signal.NEUTRAL
            desc = f"RSI at {current_rsi:.1f} (neutral zone)"

        return IndicatorResult(self.name, signal, current_rsi, desc)


class MACDIndicator:
    """MACD (Moving Average Convergence Divergence) indicator."""

    name = "MACD"

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal_period = signal

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        macd = ta.trend.MACD(
            df["close"],
            window_fast=self.fast,
            window_slow=self.slow,
            window_sign=self.signal_period
        )

        macd_line = macd.macd().iloc[-1]
        signal_line = macd.macd_signal().iloc[-1]
        histogram = macd.macd_diff().iloc[-1]

        # Check for crossover
        prev_histogram = macd.macd_diff().iloc[-2]

        if histogram > 0 and prev_histogram <= 0:
            signal = Signal.BULLISH
            desc = "MACD crossed above signal line (bullish crossover)"
        elif histogram < 0 and prev_histogram >= 0:
            signal = Signal.BEARISH
            desc = "MACD crossed below signal line (bearish crossover)"
        elif histogram > 0:
            signal = Signal.BULLISH
            desc = f"MACD above signal line (histogram: {histogram:.2f})"
        elif histogram < 0:
            signal = Signal.BEARISH
            desc = f"MACD below signal line (histogram: {histogram:.2f})"
        else:
            signal = Signal.NEUTRAL
            desc = "MACD at signal line"

        return IndicatorResult(self.name, signal, histogram, desc)


class EMAIndicator:
    """EMA Crossover indicator (fast/slow EMA)."""

    name = "EMA Crossover"

    def __init__(self, fast: int = 9, slow: int = 21):
        self.fast = fast
        self.slow = slow

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        ema_fast = ta.trend.EMAIndicator(df["close"], window=self.fast).ema_indicator()
        ema_slow = ta.trend.EMAIndicator(df["close"], window=self.slow).ema_indicator()

        current_fast = ema_fast.iloc[-1]
        current_slow = ema_slow.iloc[-1]
        prev_fast = ema_fast.iloc[-2]
        prev_slow = ema_slow.iloc[-2]

        diff = current_fast - current_slow
        prev_diff = prev_fast - prev_slow

        if diff > 0 and prev_diff <= 0:
            signal = Signal.BULLISH
            desc = f"EMA{self.fast} crossed above EMA{self.slow} (golden cross)"
        elif diff < 0 and prev_diff >= 0:
            signal = Signal.BEARISH
            desc = f"EMA{self.fast} crossed below EMA{self.slow} (death cross)"
        elif diff > 0:
            signal = Signal.BULLISH
            desc = f"EMA{self.fast} above EMA{self.slow} (uptrend)"
        elif diff < 0:
            signal = Signal.BEARISH
            desc = f"EMA{self.fast} below EMA{self.slow} (downtrend)"
        else:
            signal = Signal.NEUTRAL
            desc = "EMAs converged"

        return IndicatorResult(self.name, signal, diff, desc)


class BollingerBandsIndicator:
    """Bollinger Bands indicator."""

    name = "Bollinger Bands"

    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        bb = ta.volatility.BollingerBands(
            df["close"],
            window=self.period,
            window_dev=self.std_dev
        )

        upper = bb.bollinger_hband().iloc[-1]
        lower = bb.bollinger_lband().iloc[-1]
        middle = bb.bollinger_mavg().iloc[-1]
        current_price = df["close"].iloc[-1]

        # Calculate position within bands (0 = lower, 1 = upper)
        band_position = (current_price - lower) / (upper - lower)

        if current_price <= lower:
            signal = Signal.BULLISH  # Price at/below lower band
            desc = f"Price at lower Bollinger Band (potential bounce)"
        elif current_price >= upper:
            signal = Signal.BEARISH  # Price at/above upper band
            desc = f"Price at upper Bollinger Band (potential pullback)"
        elif band_position < 0.3:
            signal = Signal.BULLISH
            desc = f"Price near lower band ({band_position:.0%} of range)"
        elif band_position > 0.7:
            signal = Signal.BEARISH
            desc = f"Price near upper band ({band_position:.0%} of range)"
        else:
            signal = Signal.NEUTRAL
            desc = f"Price in middle of bands ({band_position:.0%} of range)"

        return IndicatorResult(self.name, signal, band_position, desc)


class StochasticIndicator:
    """Stochastic Oscillator indicator."""

    name = "Stochastic"

    def __init__(self, k_period: int = 14, d_period: int = 3, oversold: float = 20, overbought: float = 80):
        self.k_period = k_period
        self.d_period = d_period
        self.oversold = oversold
        self.overbought = overbought

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        stoch = ta.momentum.StochasticOscillator(
            df["high"],
            df["low"],
            df["close"],
            window=self.k_period,
            smooth_window=self.d_period
        )

        k = stoch.stoch().iloc[-1]
        d = stoch.stoch_signal().iloc[-1]

        if k < self.oversold and d < self.oversold:
            signal = Signal.BULLISH
            desc = f"Stochastic oversold (K:{k:.1f}, D:{d:.1f})"
        elif k > self.overbought and d > self.overbought:
            signal = Signal.BEARISH
            desc = f"Stochastic overbought (K:{k:.1f}, D:{d:.1f})"
        elif k > d and k < self.oversold + 10:
            signal = Signal.BULLISH
            desc = f"Stochastic K crossed above D in low zone"
        elif k < d and k > self.overbought - 10:
            signal = Signal.BEARISH
            desc = f"Stochastic K crossed below D in high zone"
        else:
            signal = Signal.NEUTRAL
            desc = f"Stochastic neutral (K:{k:.1f}, D:{d:.1f})"

        return IndicatorResult(self.name, signal, k, desc)


class ADXIndicator:
    """Average Directional Index - trend strength indicator."""

    name = "ADX"

    def __init__(self, period: int = 14, trend_threshold: float = 25):
        self.period = period
        self.trend_threshold = trend_threshold

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        adx = ta.trend.ADXIndicator(
            df["high"],
            df["low"],
            df["close"],
            window=self.period
        )

        adx_value = adx.adx().iloc[-1]
        plus_di = adx.adx_pos().iloc[-1]
        minus_di = adx.adx_neg().iloc[-1]

        if adx_value > self.trend_threshold:
            if plus_di > minus_di:
                signal = Signal.BULLISH
                desc = f"Strong uptrend (ADX:{adx_value:.1f}, +DI:{plus_di:.1f} > -DI:{minus_di:.1f})"
            else:
                signal = Signal.BEARISH
                desc = f"Strong downtrend (ADX:{adx_value:.1f}, -DI:{minus_di:.1f} > +DI:{plus_di:.1f})"
        else:
            signal = Signal.NEUTRAL
            desc = f"Weak/no trend (ADX:{adx_value:.1f} < {self.trend_threshold})"

        return IndicatorResult(self.name, signal, adx_value, desc)


class VolumeIndicator:
    """Volume analysis - compares current volume to average."""

    name = "Volume"

    def __init__(self, period: int = 20, high_threshold: float = 1.5):
        self.period = period
        self.high_threshold = high_threshold

    def analyze(self, df: pd.DataFrame) -> IndicatorResult:
        avg_volume = df["volume"].rolling(window=self.period).mean().iloc[-1]
        current_volume = df["volume"].iloc[-1]
        price_change = df["close"].iloc[-1] - df["close"].iloc[-2]

        volume_ratio = current_volume / avg_volume

        if volume_ratio > self.high_threshold:
            if price_change > 0:
                signal = Signal.BULLISH
                desc = f"High volume on up move ({volume_ratio:.1f}x average)"
            else:
                signal = Signal.BEARISH
                desc = f"High volume on down move ({volume_ratio:.1f}x average)"
        else:
            signal = Signal.NEUTRAL
            desc = f"Normal volume ({volume_ratio:.1f}x average)"

        return IndicatorResult(self.name, signal, volume_ratio, desc)


def get_default_indicators() -> list[Indicator]:
    """Get the default set of indicators."""
    return [
        RSIIndicator(),
        MACDIndicator(),
        EMAIndicator(),
        BollingerBandsIndicator(),
        StochasticIndicator(),
        ADXIndicator(),
        VolumeIndicator(),
    ]
