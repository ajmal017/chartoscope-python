from chartoscope.core.common import *
from chartoscope.core.library import *

import random

def test_hma_series():
    hma1 = HmaIndicator(10)
    previous_value = 100
    for i in range(31):
        current_value = previous_value + random.randint(-3, 3)
        print(hma1.calculate(Timestamp(2017, 1, i), current_value))
        previous_value = current_value

    print(hma1.series())
    assert(not hma1.series().empty)

