from chartoscope.core.common import *


class SmaCalculator(LookBehindPool):
    def __init__(self, capacity, period):
        super().__init__(capacity, lambda: None)
        self._valuePool = LookBehindPool(capacity, lambda: None)
        self._period = period

    def calculate(self, value):
        self._valuePool.write_forward(value)

        if self._valuePool.length >= self._period:
            sma_value = sum(self._valuePool.read_back(self._period)) / self._period

            self.write_forward(sma_value)

            return sma_value
        else:
            return None

    @property
    def period(self):
        return self._period


class SmaItem:
    def __init__(self):
        self.timestamp = None
        self.value = None

    def write(self, timestamp_value, item_value):
        self.timestamp = timestamp_value
        self.value = item_value


class SmaIndicator(MovingAverage, LookBehindPool, DataFrame):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: SmaItem())
        self._smaCalculator = SmaCalculator(capacity, period)

    def calculate(self, timestamp_value, input_value):
        sma_value = self._smaCalculator.calculate(input_value)
        if sma_value is not None:
            self.set_forward(lambda item: item.write(timestamp_value, sma_value))

        return sma_value

    @property
    def period(self):
        return self._smaCalculator.period

    def back_fill(self, sma_file_reader):
        result = sma_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            self._moveNext()
            result = sma_file_reader.read()

    @property
    def label(self):
        return 'sma({})'.format(self.period)


class SmaFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('sma', BinaryFileHeaderFormat('iif'))


class SmaFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, SmaFileInfo())

    def append(self, timestamp_value, sma_value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], sma_value)
        self._append(row_data)


SmaFileRecord = namedtuple("SmaFileRecord", "timestamp value")


class SmaFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, SmaFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return SmaFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
