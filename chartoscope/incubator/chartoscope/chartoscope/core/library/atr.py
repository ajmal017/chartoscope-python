from chartoscope.core.common import *
from chartoscope.core.library import *

import pandas as pd


class AtrHlcPoolItem:
    def __init__(self):
        self._high = None
        self._low = None
        self._close = None

    def write(self, high, low, close):
        self._high = high
        self._low = low
        self._close = close

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close


class AtrCalculator(LookBehindPool):
    def __init__(self, capacity, period):
        super().__init__(capacity, lambda: None)
        self._hlc_pool = LookBehindPool(2, lambda: AtrHlcPoolItem())
        self._tr_pool = LookBehindPool(period, lambda: None)
        self._period = period

    def calculate(self, ohlc_bar):
        self._hlc_pool.set_forward(lambda item: item.write(ohlc_bar.high, ohlc_bar.low, ohlc_bar.close))

        if self._tr_pool.has_value:
            true_range = max(ohlc_bar.high - ohlc_bar.low, abs(ohlc_bar.high - self._hlc_pool.previous.close),
                             abs(ohlc_bar.low - self._hlc_pool.previous.close))
        else:
            true_range = ohlc_bar.high - ohlc_bar.low

        self._tr_pool.write_forward(true_range)

        if self._tr_pool.length >= self._period:
            total = 0
            index = 0
            while index < self._period:
                total += self._tr_pool[index]
                index += 1

            average = total / self._period

            self.write_forward(average)

            return average
        else:
            return None


class AtrItem:
    def __init__(self):
        self.timestamp = None
        self.value = None

    def write(self, timestamp_value, value):
        self.timestamp = timestamp_value
        self.value = value


class AtrIndicator(LookBehindPool):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: AtrItem())
        self._atr_calculator = AtrCalculator(capacity, period)

    def calculate(self, timestamp_value, ohlc_bar):
        atr_value = self._atr_calculator.calculate(ohlc_bar)
        if atr_value is not None:
            self.set_forward(lambda item: item.write(timestamp_value, atr_value))

        return atr_value

    def series(self, timestamp_format='%Y%m%d %H:%M:%S'):
        index = 0
        index_names = []
        values = []
        while index < self.length:
            index_names.append(self[index].timestamp.to_string(timestamp_format))
            values.append(self[index].value)
            index += 1

        return pd.Series(values, index_names)

    def back_fill(self, atr_file_reader):
        result = atr_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            result = atr_file_reader.read()


class AtrFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('atr', BinaryFileHeaderFormat('iif'))


class AtrFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, AtrFileInfo())

    def append(self, timestamp_value, value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.header_format.format, date_time_split[0], date_time_split[1], value)
        self._append(row_data)

AtrFileRecord = namedtuple("AtrFileRecord", "timestamp value")


class AtrFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, AtrFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return AtrFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
