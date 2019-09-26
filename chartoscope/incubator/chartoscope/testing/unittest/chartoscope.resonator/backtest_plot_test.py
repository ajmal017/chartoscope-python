from chartoscope import Backtest
from chartoscope import Ohlc, PriceFeeder, TimeframeInterval

def test_backtest_plot():
    Backtest.plot(Ohlc(TimeframeInterval.M1), PriceFeeder())