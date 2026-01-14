"""Confluence detection - aggregate signals from multiple indicators."""

from dataclasses import dataclass

import pandas as pd

from .indicators import Indicator, IndicatorResult, Signal, get_default_indicators


@dataclass
class ConfluenceResult:
    """Result from confluence analysis."""
    bullish_count: int
    bearish_count: int
    neutral_count: int
    total_indicators: int
    indicator_results: list[IndicatorResult]
    current_price: float
    symbol: str

    @property
    def bullish_percentage(self) -> float:
        """Percentage of indicators showing bullish signal."""
        return self.bullish_count / self.total_indicators * 100

    @property
    def bearish_percentage(self) -> float:
        """Percentage of indicators showing bearish signal."""
        return self.bearish_count / self.total_indicators * 100

    @property
    def dominant_signal(self) -> Signal:
        """Get the dominant signal direction."""
        if self.bullish_count > self.bearish_count:
            return Signal.BULLISH
        elif self.bearish_count > self.bullish_count:
            return Signal.BEARISH
        return Signal.NEUTRAL

    def has_confluence(self, min_agreement: int) -> bool:
        """Check if there's confluence (min indicators agreeing)."""
        return self.bullish_count >= min_agreement or self.bearish_count >= min_agreement

    def get_confluence_direction(self, min_agreement: int) -> Signal | None:
        """Get the direction of confluence if it exists."""
        if self.bullish_count >= min_agreement:
            return Signal.BULLISH
        elif self.bearish_count >= min_agreement:
            return Signal.BEARISH
        return None


class ConfluenceDetector:
    """Detects confluence across multiple indicators."""

    def __init__(self, indicators: list[Indicator] | None = None):
        self.indicators = indicators or get_default_indicators()

    def analyze(self, df: pd.DataFrame, symbol: str = "BTCUSDT") -> ConfluenceResult:
        """
        Analyze price data with all indicators and return confluence result.

        Args:
            df: DataFrame with OHLCV data
            symbol: Trading pair symbol

        Returns:
            ConfluenceResult with all indicator signals
        """
        results = []
        bullish = 0
        bearish = 0
        neutral = 0

        for indicator in self.indicators:
            try:
                result = indicator.analyze(df)
                results.append(result)

                if result.signal == Signal.BULLISH:
                    bullish += 1
                elif result.signal == Signal.BEARISH:
                    bearish += 1
                else:
                    neutral += 1
            except Exception as e:
                # Log error but continue with other indicators
                print(f"Error analyzing {indicator.name}: {e}")

        return ConfluenceResult(
            bullish_count=bullish,
            bearish_count=bearish,
            neutral_count=neutral,
            total_indicators=len(self.indicators),
            indicator_results=results,
            current_price=df["close"].iloc[-1],
            symbol=symbol,
        )
