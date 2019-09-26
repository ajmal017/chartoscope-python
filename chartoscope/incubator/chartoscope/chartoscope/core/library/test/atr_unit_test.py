from chartoscope.core.library import *
from nose.tools import *
import random


def test_macd_calculation_works():
    atr_indicator = AtrIndicator(14)
    previous_price = 100
    for i in range(14):
        current_price = previous_price + random.randint(-3, 3)
        open_price = current_price
        high_price = current_price + random.randint(0, 3)
        low_price = current_price - random.randint(0, 3)
        close_price = random.randint(low_price, high_price)

        ohlc_bar = OhlcBarItem()
        ohlc_bar.set(Timestamp(2017, 1, i), open_price, high_price, low_price, close_price)

        print(atr_indicator .calculate(Timestamp(2017, 1, i), ohlc_bar))
        previous_price = current_price

    assert_true(atr_indicator.has_value)


def test_macd_signal_line_cross_works():
    pass

