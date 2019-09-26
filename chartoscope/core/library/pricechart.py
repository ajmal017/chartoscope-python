import pandas as pd
from chartoscope.core.common import LookBehindPool

from enum import Enum


class PriceChartType(Enum):
    Ohlc = 1
    HeikenAshi = 2
    Candlestick = 3
    Renko = 4
    Range = 5


class PriceChart(LookBehindPool):
    def __init__(self, capacity, item_init_lambda):
        super().__init__(capacity, item_init_lambda)

    def series(self, timestamp_format='%Y%m%d %H:%M:%S'):
        index = 0
        index_names = []
        values = []
        while index < self.length:
            index_names.append(self[index].timestamp.to_string(timestamp_format))
            values.append(self[index].close)
            index += 1

        return pd.Series(values, index_names)
