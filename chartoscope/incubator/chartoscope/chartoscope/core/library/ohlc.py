from chartoscope.core.common import *


class OHLCPriceOption(Enum):
    All = 0
    Open = 1
    High = 2
    Low = 3
    Close = 4


class OhlcBarItem:
    def __init__(self):
        self._timestamp = None
        self._open = None
        self._high = None
        self._low = None
        self._close = None

    def set(self, timestamp_value, open_price, high_price, low_price, close_price):
        self._timestamp = timestamp_value
        self._open = open_price
        self._high = high_price
        self._low = low_price
        self._close = close_price

    @property
    def is_bullish_candle(self):
        return self._close > self._open

    @property
    def is_bearish_candle(self):
        return self._close < self._open

    @property
    def timestamp(self):
        return self.timestamp

    @property
    def open(self):
        return self._open

    @property
    def high(self):
        return self._high

    @property
    def low(self):
        return self._low

    @property
    def close(self):
        return self._close


class OhlcBars(LookBehindPool):
    def __init__(self, capacity):
        super().__init__(capacity, lambda: OhlcBarItem())
        self._technicals = Technicals(lambda: self.current)

    def write(self, timestamp_value, open_price, high_price, low_price, close_price):
        self.set_forward(lambda item: item.set(timestamp_value, open_price, high_price, low_price, close_price))

        for technical in self._technicals:
            technical.calculate(timestamp_value, close_price)


class Ohlc(PriceAction):
    def __init__(self, feed_interval, on_price_action=None, capacity=PoolConfig.instance().DefaultPriceChartPoolSize):
        super().__init__(PriceChartType.Ohlc, OhlcAggregator(feed_interval), OhlcBars(capacity))
        self._on_price_action = on_price_action
        self._initialized = False

    def price_action(self, timestamp_value, bid, ask):
        last_price_bar_sequence = self._price_bars.sequence
        if self._initialized:
            self._aggregator.price_action(timestamp_value, bid, ask, self._price_bars)
        else:
            self._aggregator.initialize(timestamp_value, bid, ask)
            self._initialized = True
        if self._on_price_action is not None and self._price_bars.sequence > last_price_bar_sequence:
            self._on_price_action(self._price_bars.current, self._price_bars)

    def back_fill(self, timestamp_value, open_price, high_price, low_price, close_price):
        self._price_bars.write(timestamp_value, open_price, high_price, low_price, close_price)


class OhlcAggregator:
    def __init__(self, timeframe_value):
        self._timeframe = timeframe_value
        self._previous_price = None
        self._open = None
        self._high = None
        self._low = None
        self._next_ticks = None

    def initialize(self, timestamp_value, bid, ask):
        self._next_ticks = self.get_next_ticks(self._timeframe.timeUnit, timestamp_value)

        current_price = (bid + ask) / 2
        self._previous_price = current_price
        self._open = current_price
        self._high = current_price
        self._low = current_price

    def price_action(self, timestamp_value, bid, ask, ohlcbars):
        current_price = (bid + ask) / 2

        if timestamp_value.ticks < self._next_ticks:
            if current_price > self._high:
                self._high = current_price
            elif current_price < self._low:
                self._low = current_price
        else:
            ohlcbars.write(TimestampConverter.from_ticks(self._next_ticks), self._open, self._high, self._low,
                           self._previous_price)

            self._open = self._previous_price
            self._high = current_price
            self._low = current_price

            self._next_ticks = self.get_next_ticks(self._timeframe.time_unit, timestamp_value)

        self._previous_price = current_price

    def get_next_ticks(self, time_unit, timestamp_value):
        if time_unit == TimeUnit.Minute:
            return TimestampConverter.next_minute_ticks(timestamp_value.year, timestamp_value.month,
                                                        timestamp_value.day, timestamp_value.hour,
                                                        timestamp_value.minute, self._timeframe.units)
        elif time_unit == TimeUnit.Hour:
            return TimestampConverter.next_hour_ticks(timestamp_value.year, timestamp_value.month, timestamp_value.day,
                                                      timestamp_value.hour, self._timeframe.units)
        elif time_unit == TimeUnit.Day:
            return TimestampConverter.next_day_ticks(timestamp_value.year, timestamp_value.month, timestamp_value.day,
                                                     self._timeframe.units)
        elif time_unit == TimeUnit.Month:
            return TimestampConverter.next_month_ticks(timestamp_value.year, timestamp_value.month,
                                                       self._timeframe.units)
        else:
            return None


class OhlcFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('ohlc', BinaryFileHeaderFormat('iiffff'))


class OhlcFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, OhlcFileInfo())

    def append(self, timestamp_value, open_price, high_price, low_price, close_price):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1], open_price,
                               high_price, low_price, close_price)
        self._append(row_data)

OhlcFileRecord = namedtuple("OhlcFileRecord", "timestamp, open, high, low, close")


class OhlcFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, OhlcFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return OhlcFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2], data[3], data[4],
                                  data[5])
