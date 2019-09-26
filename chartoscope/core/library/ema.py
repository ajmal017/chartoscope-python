from chartoscope.core.library import *


class EmaCalculator(LookBehindPool):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultCalculatorPoolSize):
        super().__init__(capacity, lambda: None)
        self._value_pool = LookBehindPool(capacity, lambda: None)
        self._period = period
        self._smoothing_constant = 2 / (period + 1)

    def calculate(self, value):
        self._value_pool.write_forward(value)

        if self._value_pool.length >= self._period:
            average = sum(self._value_pool.read_back(self._period)) / self._period

            previous_ema = average if self.length == 0 else self.current
            ema_value = (value * self._smoothing_constant) + (previous_ema * (1 - self._smoothing_constant))

            self.write_forward(ema_value)

            return average
        else:
            return None


class EmaItem:
    def __init__(self):
        self.timestamp = None
        self.value = None

    def write(self, timestamp_value, item_value):
        self.timestamp = timestamp_value
        self.value = item_value


class EmaIndicator(MovingAverage, DataFrame):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: EmaItem())
        self._ema_calculator = EmaCalculator(period, capacity)

    def calculate(self, timestamp_value, input_value):
        ema_value = self._ema_calculator.calculate(input_value)
        if ema_value is not None:
            self.set_forward(lambda item: item.write(timestamp_value, ema_value))

        return ema_value

    def backfill(self, ema_file_reader):
        result = ema_file_reader.read()
        while result is not None:
            self._pool[self._current_position].set(result[0], result[1])
            self._moveNext()
            result = ema_file_reader.read()

        
class EmaFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('ema', BinaryFileHeaderFormat('iif'))


class EmaFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, EmaFileInfo())

    def append(self, timestamp_value, ema_value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], ema_value)
        self._append(row_data)

EmaFileRecord = namedtuple("EmaFileRecord", "timestamp value")


class EmaFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, EmaFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return EmaFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
