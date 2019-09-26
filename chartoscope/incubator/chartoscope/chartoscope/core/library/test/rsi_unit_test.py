from chartoscope.core.common import *
from chartoscope.core.library import *
import random

def test_rsi_series():
    rsi = RsiIndicator(14)

    print(rsi.calculate(Timestamp(2009, 12, 14), 44.34))
    print(rsi.calculate(Timestamp(2009, 12, 15), 44.09))
    print(rsi.calculate(Timestamp(2009, 12, 16), 44.15))
    print(rsi.calculate(Timestamp(2009, 12, 17), 44.61))
    print(rsi.calculate(Timestamp(2009, 12, 18), 44.33))
    print(rsi.calculate(Timestamp(2009, 12, 21), 44.83))
    print(rsi.calculate(Timestamp(2009, 12, 22), 45.10))
    print(rsi.calculate(Timestamp(2009, 12, 23), 45.42))
    print(rsi.calculate(Timestamp(2009, 12, 24), 45.84))
    print(rsi.calculate(Timestamp(2009, 12, 28), 46.08))
    print(rsi.calculate(Timestamp(2009, 12, 29), 45.89))
    print(rsi.calculate(Timestamp(2009, 12, 30), 46.03))
    print(rsi.calculate(Timestamp(2009, 12, 31), 45.61))
    print(rsi.calculate(Timestamp(2010, 1, 4), 46.28))
    print(rsi.calculate(Timestamp(2010, 1, 5), 46.28))
    print(rsi.calculate(Timestamp(2010, 1, 6), 46.00))
    print(rsi.calculate(Timestamp(2010, 1, 7), 46.03))
    print(rsi.calculate(Timestamp(2010, 1, 8), 46.41))

    rsi_series = rsi.series(lambda item: item.relative_strength_index)
    print(rsi_series)
    assert(not rsi_series.empty)

