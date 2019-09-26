from chartoscope.core.common import *
from chartoscope.core.library import *
from collections import namedtuple
import enum


class StockBarOption(Enum):
    All = 0
    Open = 1
    High = 2
    Low = 3
    Close = 4
    Volume = 5


class StockBarItem:
    def __init__(self):
        self._timestamp = None
        self._open = None
        self._high = None
        self._low = None
        self._close = None
        self._volume = None

    def write(self, timestamp_value, open_price, high_price, low_price, close_price, volume):
        self._timestamp = timestamp_value
        self._open = open_price
        self._high = high_price
        self._low = low_price
        self._close = close_price
        self._volume = volume

    @property
    def is_bullish(self):
        return self._close > self._open

    def is_bearish(self):
        return self._close < self._open


class StockBars(PriceChart, LookBehindPool):
    def __init__(self, capacity=PoolConfig.instance().DefaultPriceChartPoolSize):
        super().__init__(capacity, lambda: StockBarItem())
        self.technicals = Technicals(lambda: self.current)

    def register(self, ta_function, value_item_lambda):
        self.technicals.register(ta_function, value_item_lambda)

    def write(self, timestamp_value, open_price, high_price, low_price, close_price):
        self.set_forward(lambda item: item.write(timestamp_value, open_price, high_price, low_price, close_price))

        for technical in self.technicals:
            technical.ta_function.calculate(timestamp_value, technical.value_item_lambda(technical.price_bar_lambda()))


class Stock(PriceAction):
    def __init__(self, ticker_reference, on_price_action=None, capacity=PoolConfig.instance().DefaultPriceChartPoolSize):
        super().__init__(PriceChartType.Stock, StockAggregator(ticker_reference.interval), StockBars(capacity))
        self._on_price_action = on_price_action
        self._initialized = False
        self._technicals = self._price_bars.technicals
        self._tickerReference = ticker_reference

    def price_action(self, timestamp_value, bid, ask):
        last_price_bar_sequence = self._price_bars.sequence
        if self._initialized:
            self._aggregator.price_action(timestamp_value, bid, ask, self._price_bars)
        else:
            self._aggregator.initialize(timestamp_value, bid, ask)
            self._initialized = True
        if self._on_price_action is not None and self._price_bars.sequence > last_price_bar_sequence:
            self._on_price_action(self._tickerReference, self._price_bars.current, self._price_bars)

    def back_fill(self, timestamp_value, open_price, high_price, low_price, close_price):
        self._price_bars.write(timestamp_value, open_price, high_price, low_price, close_price)


class StockAggregator:
    def __init__(self, timeframe_value):
        self._timeframe = timeframe_value.interval
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

    def price_action(self, timestamp_value, bid, ask, volume, stock_bars):
        current_price = (bid + ask) / 2

        if timestamp_value.ticks < self._next_ticks:
            if current_price > self._high:
                self._high = current_price
            elif current_price < self._low:
                self._low = current_price
        else:
            stock_bars.write(TimestampConverter.from_ticks(self._next_ticks), self._open, self._high, self._low,
                             self._previous_price, volume)

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


class StockFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('stock')


class StockFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, StockFileInfo())

    def append(self, timestamp_value, open_price, high_price, low_price, close_price, adjusted_close, volume):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.header_format.format, date_time_split[0], date_time_split[1], open_price,
                               high_price, low_price, close_price, adjusted_close, volume)
        self._append(row_data)

StockFileRecord = namedtuple('StockFileRecord', 'timestamp open high low close adjusted_close volume')


class StockFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, StockFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return StockFileRecord(TimestampConverter.from_tick_split(data[0], data[1], 0), data[2], data[3], data[4],
                                   data[5], data[6], data[7])


class StockPublisher:
    def __init__(self, on_price_action=None):
        self._on_price_action = on_price_action
        self._price_feeds = {}
        self._price_bars = {}
        self._ticker_references = []

    def setup(self, ticker_reference, pool_size=PoolConfig.instance().DefaultPoolSize):
        self._ticker_references.append(ticker_reference)

        price_bar = StockBars(pool_size)
        self._price_bars[ticker_reference.id] = price_bar

        aggregator = Stock(ticker_reference, lambda ticker_ref, current_price, price_history:
                           self.price_action(ticker_ref, current_price, price_history))
        self._price_feeds[ticker_reference.id] = aggregator
        return price_bar

    def price_action(self, ticker_reference, current_price, price_history):
        self._price_bars[ticker_reference.id].write(current_price.timestamp, current_price.open, current_price.high,
                                                    current_price.low, current_price.close)
        if self._on_price_action is not None:
            self._on_price_action(ticker_reference, current_price, price_history)
