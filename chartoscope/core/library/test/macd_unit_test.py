from chartoscope.core.library import *
from nose.tools import *
import random


def test_macd_calculation_works():
    macd_indicator = MacdIndicator(21, 12, 5)
    previous_value = 100
    for i in range(25):
        current_value = previous_value + random.randint(-1, 1)
        print(macd_indicator.calculate(Timestamp(2017, 1, i), current_value))
        previous_value = current_value

    assert_true(macd_indicator.has_value)



def test_macd_signal_line_cross_works():
    pass
