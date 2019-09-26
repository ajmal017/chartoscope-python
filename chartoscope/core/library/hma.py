from chartoscope.core.common import *
from chartoscope.core.library import *


class HmaCalculator(LookBehindPool):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultCalculatorPoolSize):
        super().__init__(capacity, lambda: None)
        if period <= 1:
            raise Exception("HMA period must be greater than 1")
        self._half_period_wma = WmaCalculator(period // 2, capacity)
        self._full_period_wma = WmaCalculator(period, capacity)
        self._delta_wma = WmaCalculator(int(math.sqrt(period)), capacity)
        self._period = period
        weight_values = [period - i for i in range(period)]
        total_weights = sum(weight_values)
        self._weight_factors = list(map(lambda x: x/total_weights, weight_values))

    def calculate(self, value):
        half_period_wma = self._half_period_wma.calculate(value)
        full_period_wma = self._full_period_wma.calculate(value)
        if half_period_wma is not None and full_period_wma is not None:
            delta_wma = (half_period_wma * 2) - full_period_wma
            hma_value = self._delta_wma.calculate(delta_wma)
            if hma_value is not None:
                self.write_forward(hma_value)
                return hma_value
            else:
                return None
        else:
            return None


class HmaItem:
    def __init__(self):
        self.timestamp = None
        self.value = None

    def write(self, timestamp_value, input_value):
        self.timestamp = timestamp_value
        self.value = input_value


class HmaIndicator(MovingAverage, LookBehindPool, DataFrame):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: HmaItem())

        self._hma_calculator = HmaCalculator(period, capacity)

    def calculate(self, timestamp_value, value, back_fill=False):
        hma_value = self._hma_calculator.calculate(value)
        if hma_value is not None and not back_fill:
            self.set_forward(lambda item: item.write(timestamp_value, hma_value))

        return hma_value

    def back_fill(self, hma_file_reader):
        result = hma_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            result = hma_file_reader.read()

    @property
    def has_reversed(self):
        return self.is_valid_index(2) and \
               ((self[2].value < self.previous.value and self.previous.value > self.current.value) or \
                (self[2].value > self.previous.value and self.previous.value < self.current.value))

    @property
    def is_upward_slope(self):
        return self.is_valid_index(1) and self.previous.value < self.current.value

    @property
    def is_downward_slope(self):
        return self.is_valid_index(1) and self.previous.value > self.current.value

    @property
    def rate_of_change(self):
        if self.is_valid_index(7):
            return (((self.current.value - self[7].value) / self[7].value) * 100) * 10000
        else:
            return 0


class HmaFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('hma', BinaryFileHeaderFormat('iif'))


class HmaFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, HmaFileInfo())

    def append(self, timestamp_value, hma_value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], hma_value)
        self._append(row_data)

HmaFileRecord = namedtuple("HmaFileRecord", "timestamp value")


class HmaFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, HmaFileInfo())

    def read(self):
        data = self._read()
        if data is not None:
            return None
        else:
            return HmaFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
