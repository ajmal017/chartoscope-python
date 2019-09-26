from chartoscope.core.common import *
from chartoscope.core.library import *

def test_ema_crossing():
    ema1= EmaIndicator(2)
    ema2= EmaIndicator(3)

    ema1.calculate(Timestamp(2017, 1, 1), 1)
    ema1.calculate(Timestamp(2017, 1, 2), 2)
    ema1.calculate(Timestamp(2017, 1, 3), 3)
    ema1.calculate(Timestamp(2017, 1, 4), 4)

    ema2.calculate(Timestamp(2017, 1, 1), 4)
    ema2.calculate(Timestamp(2017, 1, 2), 3)
    ema2.calculate(Timestamp(2017, 1, 3), 2)
    ema2.calculate(Timestamp(2017, 1, 4), 1)

    assert(ema1.crosses(ema2))
    assert(ema2.crosses(ema1))

    assert(ema1.crosses_above(ema2))
    assert(ema2.crosses_below(ema1))

def test_ema_series():
    ema1 = EmaIndicator(2)

    ema1.calculate(Timestamp(2017, 1, 1), 1)
    ema1.calculate(Timestamp(2017, 1, 2), 2)
    ema1.calculate(Timestamp(2017, 1, 3), 3)
    ema1.calculate(Timestamp(2017, 1, 4), 4)

    print(ema1.series())
    assert(not ema1.series().empty)

