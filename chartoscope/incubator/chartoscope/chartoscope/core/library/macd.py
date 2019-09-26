from chartoscope.core.library import *

MacdCalculationResult = namedtuple('MacdPeriods', 'slow_ema fast_ema signal_ema')


class MacdCalculator(LookBehindPool):
    def __init__(self, slow_moving_period, fast_moving_period, capacity=100):
        super().__init__(capacity, lambda: None)
        self._pricePool = LookBehindPool(capacity, lambda: None)

        self._slow_moving_period = slow_moving_period
        self._slow_moving_ema = EmaCalculator(slow_moving_period, capacity)

        self._fastMovingPeriod = fast_moving_period
        self._fast_moving_ema = EmaCalculator(fast_moving_period, capacity)

    def calculate(self, value):
        self._pricePool.write_forward(value)

        self._slow_moving_ema.calculate(value)
        self._fast_moving_ema.calculate(value)

        if self._slow_moving_ema.has_value and self._fast_moving_ema.has_value:
            macd_value = self._fast_moving_ema.current - self._slow_moving_ema.current

            self.write_forward(macd_value)

            return MacdCalculationResult(macd_value, self._slow_moving_ema.current, self._fast_moving_ema.current)
        else:
            return None


class MacdIndicatorItem:
    def __init__(self):
        self._timestamp = None
        self._slow_ema = None
        self._fast_ema = None
        self._signal_line_ema = None

    def write(self, timestamp_value, slow_ema, fast_ema, signal_line):
        self._timestamp = timestamp_value
        self._slow_ema = slow_ema
        self._fast_ema = fast_ema
        self._signal_line_ema = signal_line

    @property
    def macd(self):
        return self._fast_ema - self._slow_ema

    @property
    def histogram(self):
        return self.macd - self._signal_line_ema

    @property
    def signal_line(self):
        return self._signal_line_ema


class MacdIndicator(LookBehindPool, Indicator, DataFrame):
    def __init__(self, slow_moving_period, fast_moving_period, signal_line_period,
                 capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: MacdIndicatorItem())
        self._slow_moving_period = slow_moving_period
        self._fast_moving_period = fast_moving_period
        self._macd_calculator = MacdCalculator(slow_moving_period, fast_moving_period, capacity)
        self._signal_line_period = signal_line_period
        self._signal_line_ema = EmaCalculator(signal_line_period, capacity)

    def calculate(self, timestamp_value, input_value):
        result = self._macd_calculator.calculate(input_value)
        if result is not None:
            ema_value = self._signal_line_ema.calculate(result[0])
            if ema_value is not None:
                self.set_forward(lambda item: item.write(timestamp_value, result[1], result[2], ema_value))

                return result[0]
            else:
                return None
        else:
            return None

    @property
    def fast_moving_period(self):
        return self._fast_moving_period

    @property
    def slow_moving_period(self):
        return self._slow_moving_period

    @property
    def signal_line_period(self):
        return self._signal_line_period

    @property
    def is_bullish_crossing(self):
        return self.length > 1 and self.current.signal_line < self.current.macd and \
               self.previous.signal_line < self.previous.macd

    @property
    def is_bearish_crossing(self):
        return self.length > 1 and self.current.signal_line > self.current.macd and \
               self.previous.signal_line > self.previous.macd

    def back_fill(self, macd_file_reader):
        result = macd_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            result = macd_file_reader.read()


class MacdFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('macd', BinaryFileHeaderFormat('iifff'))


class MacdFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, MacdFileInfo())

    def append(self, timestamp_value, slow_ema, fast_ema, signal_line):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], slow_ema,
                               fast_ema, signal_line)
        self._append(row_data)

MacdFileRecord = namedtuple("MacdFileRecord", "timestamp slow_ema, fast_ema, signal_line_ema")


class MacdFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, MacdFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return MacdFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2], data[3], data[4])
