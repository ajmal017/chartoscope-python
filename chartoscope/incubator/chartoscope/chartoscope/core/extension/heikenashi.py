from enum import Enum
from chartoscope.core.library import *


class HeikenAshiPriceOption(Enum):
    All = 0
    Open = 1
    High = 2
    Low = 3
    Close = 4


class HeikenAshiBarItem:
    def __init__(self):
        self._timestamp = None
        self._open = None
        self._high = None
        self._low = None
        self._close = None

    def write(self, timestamp_value, open_price, high_price, low_price, close_price):
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
        return self._timestamp

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


class HeikenAshiBars(PriceChart, LookBehindPool):
    def __init__(self, capacity):
        super().__init__(capacity, lambda: HeikenAshiBarItem())
        self._technicals = Technicals(lambda: self.current)

    def register(self, ta_function, value_item_lambda):
        self._technicals.register(ta_function, value_item_lambda)

    def write(self, timestamp_value, open_price, high_price, low_price, close_price):
        self.set_forward(lambda item: item.write(timestamp_value, open_price, high_price, low_price, close_price))

        for technical in self._technicals:
            technical.ta_function.calculate(timestamp_value, technical.value_item_lambda(technical.price_bar_lambda()))

    @property
    def technicals(self):
        return self._technicals


class HeikenAshi(PriceAction):
    def __init__(self, ticker_reference, on_price_action=None, capacity=PoolConfig.instance().DefaultPriceChartPoolSize):
        super().__init__(PriceChartType.HeikenAshi, HeikenAshiAggregator(ticker_reference.interval),
                         HeikenAshiBars(capacity))
        self._on_price_action = on_price_action
        self._initialized = False
        self.technicals = self._price_bars.technicals
        self._ticker_reference = ticker_reference

    def price_action(self, timestamp_value, bid, ask):
        last_price_bar_sequence = self._price_bars.sequence
        if self._initialized:
            self._aggregator.price_action(timestamp_value, bid, ask, self._price_bars)
        else:
            self._aggregator.initialize(timestamp_value, bid, ask)
            self._initialized = True
        if self._on_price_action is not None and self._price_bars.sequence > last_price_bar_sequence:
            self._on_price_action(self._ticker_reference, self._price_bars.current, self._price_bars)

    def back_fill(self, timestamp_value, open_price, high_price, low_price, close_price):
        self._price_bars.write(timestamp_value, open_price, high_price, low_price, close_price)


class HeikenAshiAggregator:
    def __init__(self, timeframe_value):
        self._timeframe = timeframe_value.interval
        self._next_ticks = None
        self._previousPrice = None
        self._open = None
        self._high = None
        self._low = None

    def initialize(self, timestamp_value, bid, ask):
        self._next_ticks = self.get_next_ticks(self._timeframe.time_unit, timestamp_value)

        current_price = (bid + ask) / 2
        self._previousPrice = current_price
        self._open = current_price
        self._high = current_price
        self._low = current_price

    def price_action(self, timestamp_value, bid, ask, heiken_ashi_bars):
        current_price = (bid + ask) / 2

        if timestamp_value.ticks < self._next_ticks:
            if current_price > self._high:
                self._high = current_price
            elif current_price < self._low:
                self._low = current_price
        else:
            ha_close = (self._open + self._high + self._low + self._previousPrice) / 4
            ha_open = (self._open + self._previousPrice) / 2 if heiken_ashi_bars.length == 0 else \
                (heiken_ashi_bars.current.open + heiken_ashi_bars.current.close) / 2
            ha_high = max(max(self._high, ha_open), ha_close)
            ha_low = min(min(self._low, ha_open), ha_close)

            heiken_ashi_bars.write(TimestampConverter.from_ticks(self._next_ticks), ha_open, ha_high, ha_low, ha_close)

            self._open = self._previousPrice
            self._high = current_price
            self._low = current_price

            self._next_ticks = self.get_next_ticks(self._timeframe.time_unit, timestamp_value)

        self._previousPrice = current_price

    def get_next_ticks(self, time_unit, timestamp_value):
        if time_unit == TimeUnit.Minute:
            return TimestampConverter.next_minute_ticks(timestamp_value.year, timestamp_value.month,
                                                        timestamp_value.day,
                                                        timestamp_value.hour, timestamp_value.minute,
                                                        self._timeframe.units)
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


class HeikenAshiFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('heiknshi', BinaryFileHeaderFormat('iiffff'))


class HeikenAshiFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, HeikenAshiFileInfo())

    def append(self, timestamp_value, open_price, high_price, low_price, close_price):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1],
                               open_price, high_price, low_price, close_price)
        self._append(row_data)


HeikenAshiRecord = namedtuple("HeikenAshiRecord", "timestamp open high low close")


class HeikenAshiFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, HeikenAshiFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return HeikenAshiRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2], data[3], data[4],
                                    data[5])


class HeikenAshiPublisher:
    def __init__(self, on_price_action=None):
        self._on_price_action = on_price_action
        self._price_feeds = {}
        self._price_bars = {}
        self._ticker_references = []

    def setup(self, ticker_reference, pool_size=PoolConfig.instance().DefaultPriceChartPoolSize):
        self._ticker_references.append(ticker_reference)

        price_bar = HeikenAshiBars(pool_size)
        self._price_bars[ticker_reference.id] = price_bar

        aggregator = HeikenAshi(ticker_reference,
                                lambda ticker_reference_value, current_price,
                                price_history: self.price_action(ticker_reference_value, current_price,
                                                                 price_history))
        self._price_feeds[ticker_reference.id] = aggregator
        return price_bar

    def price_action(self, ticker_reference, current_price, price_history):
        self._price_bars[ticker_reference.id].write(current_price.timestamp, current_price.open,
                                                    current_price.high, current_price.low, current_price.close)
        if self._on_price_action is not None:
            self._on_price_action(ticker_reference, current_price, price_history)

    @property
    def ticker_references(self):
        return self._ticker_references

    @property
    def price_feeds(self):
        return self._price_feeds