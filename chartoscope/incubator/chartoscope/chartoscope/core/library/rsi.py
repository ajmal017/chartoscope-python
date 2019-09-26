from chartoscope.core.common import *


class RsiPriceChangeItem:
    def __init__(self):
        self._previous_price = None
        self._current_price = None

    def write(self, previous_price, current_price):
        self._previous_price = previous_price
        self._current_price = current_price

    @property
    def previous_price(self):
        return self._previous_price

    @property
    def current_price(self):
        return self._current_price

    @property
    def has_gained(self):
        return self._current_price > self._previous_price

    @property
    def has_lost(self):
        return self._current_price < self._previous_price

    @property
    def gain(self):
        return self._current_price - self._previous_price if self.has_gained else 0

    @property
    def loss(self):
        return self._previous_price - self._current_price if self.has_lost else 0


class RsiCalculatorItem:
    def __init__(self):
        self._average_gain = None
        self._average_loss = None
        self._relative_strength = None
        self._relative_strength_index = None

    def write(self, average_gain, average_loss, relative_strength, relative_strength_index):
        self._average_gain = average_gain
        self._average_loss = average_loss
        self._relative_strength = relative_strength
        self._relative_strength_index = relative_strength_index

    @property
    def average_gain(self):
        return self._average_gain

    @property
    def average_loss(self):
        return self._average_loss

    @property
    def relative_strength(self):
        return self._relative_strength

    @property
    def relative_strength_index(self):
        return self._relative_strength_index


class RsiCalculator(LookBehindPool, Calculator):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultCalculatorPoolSize):
        super().__init__(capacity, lambda: RsiCalculatorItem())
        self._period = period
        self._price_change_pool = LookBehindPool(period, lambda: RsiPriceChangeItem())

    @property
    def period(self):
        return self._period

    @property
    def is_primed(self):
        return self._price_change_pool.length >= self._period

    def calculate(self, value):
        if self._price_change_pool.has_value:
            self._price_change_pool.set_forward(lambda pool_item:
                                                pool_item.write(self._price_change_pool.current.current_price, value))
        else:
            self._price_change_pool.set_forward(lambda pool_item: pool_item.write(value, value))

        if self.is_primed:
            total_gains = 0
            total_losses = 0

            for item in self._price_change_pool.read_back(self._period):
                if item.has_gained:
                    total_gains += item.gain
                elif item.has_lost:
                    total_losses += item.loss

            if self.has_value:
                average_gain = ((self.current.average_gain * (self._period - 1)) +
                                self._price_change_pool.current.gain)/self._period
                average_loss = ((self.current.average_loss * (self._period - 1)) +
                                self._price_change_pool.current.loss)/self._period
            else:
                average_gain = total_gains/self._period
                average_loss = total_losses/self._period

            relative_strength = average_gain / average_loss

            relative_strength_index = 100 - (100/(1 + relative_strength))

            self.set_forward(lambda pool_item: pool_item.write(average_gain, average_loss, relative_strength,
                                                               relative_strength_index))

            return relative_strength_index
        else:
            return None


class RsiIndicatorItem(TimestampedItem):
    def __init__(self):
        super().__init__()
        self._relative_strength_index = None

    def write(self, timestamp_value, relative_strength_index):
        super().set(timestamp_value)
        self._relative_strength_index = relative_strength_index

    @property
    def relative_strength_index(self):
        return self._relative_strength_index


class RsiIndicator(MovingAverage, LookBehindPool, DataFrame):
    def __init__(self, period, capacity=PoolConfig.instance().DefaultPoolSize):
        super().__init__(capacity, lambda: RsiIndicatorItem())

        self._rsiCalculator = RsiCalculator(period, capacity)

    def calculate(self, timestamp_value, input_value):
        rsi_value = self._rsiCalculator.calculate(input_value)
        if rsi_value is not None:
            self.set_forward(lambda item: item.write(timestamp_value, rsi_value))

        return rsi_value

    def calculate_all(self, dataset, timestamp_index=0, value_index=1):
        for item in dataset:
            self.calculate(item[timestamp_index], item[value_index])


    def back_fill(self, rsi_file_reader):
        result = rsi_file_reader.read()
        while result is not None:
            self.set_forward(lambda item: item.set(result[0], result[1]))
            self._moveNext()
            result = rsi_file_reader.read()

    @property
    def period(self):
        return self._rsiCalculator.period


class RsiFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('rsi', BinaryFileHeaderFormat('iif'))


class RsiFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, RsiFileInfo())

    def append(self, timestamp_value, rsi_value):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], rsi_value)
        self._append(row_data)


RsiFileRecord = namedtuple("RsiFileRecord", "timestamp value")


class RsiFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, RsiFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return RsiFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2])
