from chartoscope.core.common import *


class WmaCalculator(LookBehindPool):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultCalculatorPoolSize):
        super().__init__(capacity, lambda: None)
        self._value_pool = LookBehindPool(capacity, lambda: None)
        self._period = period
        weight_values = [period - i for i in range(period)]
        total_weights = sum(weight_values)
        self._weight_factors = list(map(lambda x: x / total_weights, weight_values))

    def calculate(self, value):
        self._value_pool.write_forward(value)

        if self._value_pool.is_valid_index(self._period):
            value_list = list(self._value_pool.read_back(self._period))
            wma_value = sum([value_list[i] * self._weight_factors[i] for i in range(self._period)])
            self.write_forward(wma_value)

            return wma_value
        else:
            return None


class WmaItem:
    def __init__(self):
        self.timestamp = None
        self.value = None

    def write(self, timestamp_value, value):
        self.timestamp = timestamp_value
        self.value = value


class WmaIndicator(MovingAverage, LookBehindPool, DataFrame):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: WmaItem())

        self._wmaCalculator = WmaCalculator(period, capacity)

    def calculate(self, timestamp_value, value):
        wma_value = self._wmaCalculator.calculate(value)
        if wma_value is not None:
            self.set_forward(lambda item: item.write(timestamp_value, wma_value))

        return wma_value

    def back_fill(self, wma_file_reader):
        result = wma_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            result = wma_file_reader.read()


class WmaFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('wma', BinaryFileHeaderFormat('iif'))


class WmaFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, WmaFileInfo())

    def append(self, timestamp_value, value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], value)
        self._append(row_data)

WmaFileRecord = namedtuple("WmaFileRecord", "timestamp value")


class WmaFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, WmaFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return WmaFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
