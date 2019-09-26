from enum import Enum
from chartoscope.core.common import MarketView


class MarketPosition(Enum):
    NoPosition = 0
    Long = 1
    Short = 2

    @staticmethod
    def from_market_view(market_view):
        if market_view == MarketView.Bullish:
            return MarketPosition.Long
        elif market_view == MarketView.Bearish:
            return MarketPosition.Short
        else:
            return MarketPosition.NoPosition

    @staticmethod
    def inverse(market_position):
        if market_position == MarketPosition.Long:
            return MarketPosition.Short
        elif market_position == MarketPosition.Short:
            return MarketPosition.Long
        else:
            return MarketPosition.NoPosition
