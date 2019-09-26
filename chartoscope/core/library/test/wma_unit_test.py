from chartoscope.core.common import *
from chartoscope.core.library import *

def test_wma_series():
    wma1 = WmaIndicator(2)

    wma1.calculate(Timestamp(2017, 1, 1), 1)
    wma1.calculate(Timestamp(2017, 1, 2), 2)
    wma1.calculate(Timestamp(2017, 1, 3), 3)
    wma1.calculate(Timestamp(2017, 1, 4), 4)
    wma1.calculate(Timestamp(2017, 1, 5), 4)
    wma1.calculate(Timestamp(2017, 1, 6), 4)
    wma1.calculate(Timestamp(2017, 1, 7), 6)
    print(wma1.series())
    assert(not wma1.series().empty)

