from chartoscope.core.common import *
from chartoscope.core.library import *

def test_sma_crossing():
    sma1= SmaIndicator(2)
    sma2= SmaIndicator(3)

    sma1.calculate(Timestamp(2017, 1, 1), 1)
    sma1.calculate(Timestamp(2017, 1, 2), 2)
    sma1.calculate(Timestamp(2017, 1, 3), 3)
    sma1.calculate(Timestamp(2017, 1, 4), 4)

    sma2.calculate(Timestamp(2017, 1, 1), 4)
    sma2.calculate(Timestamp(2017, 1, 2), 3)
    sma2.calculate(Timestamp(2017, 1, 3), 2)
    sma2.calculate(Timestamp(2017, 1, 4), 1)

    assert(sma1.crosses(sma2))
    assert(sma2.crosses(sma1))

    assert(sma1.crosses_above(sma2))
    assert(sma2.crosses_below(sma1))

def test_sma_series():
    sma1 = SmaIndicator(2)

    sma1.calculate(Timestamp(2017, 1, 1), 1)
    sma1.calculate(Timestamp(2017, 1, 2), 2)
    sma1.calculate(Timestamp(2017, 1, 3), 3)
    sma1.calculate(Timestamp(2017, 1, 4), 4)

    print(sma1.series())
    assert(not sma1.series().empty)

