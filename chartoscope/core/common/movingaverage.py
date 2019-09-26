from chartoscope.core.common import *
import pandas as pd

class MovingAverage(LookBehindPool, Indicator):
    def __init__(self, capacity, item_value_lambda):
        super().__init__(capacity, item_value_lambda)

    def crosses(self, value_pool):
        return self.crosses_above(value_pool) or self.crosses_below(value_pool)

    def crosses_above(self, value_pool):
        if self.length > 1 and value_pool.length > 1:
            if self.current.timestamp.ticks == value_pool.current.timestamp.ticks and\
                    self.previous.timestamp.ticks == value_pool.previous.timestamp.ticks:
                return self.current.value > value_pool.current.value and self.previous.value < value_pool.previous.value
            else:
                raise Exception("Timestamps are out-of-sync!")
        else:
            return False

    def crosses_below(self, value_pool):
        if self.length > 1 and value_pool.length > 1:
            if self.current.timestamp.ticks == value_pool.current.timestamp.ticks and\
                    self.previous.timestamp.ticks == value_pool.previous.timestamp.ticks:
                return self.current.value < value_pool.current.value and self.previous.value > value_pool.previous.value
            else:
                raise Exception("Timestamps are out-of-sync!")
        else:
            return False

    def series(self, item_lambda=None, timestamp_format='%Y%m%d %H:%M:%S'):
        index = 0
        index_names = []
        values = []
        while index < self.length:
            index_names.append(self[index].timestamp.to_string(timestamp_format))
            if item_lambda is None:
                values.append(self[index].value)
            else:
                values.append(item_lambda(self[index]))
            index += 1

        return pd.Series(values, index_names)
