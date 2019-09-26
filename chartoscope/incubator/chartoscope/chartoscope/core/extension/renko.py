from chartoscope.core.library import *


class RenkoPriceOption(Enum):
    All = 0
    Open = 1
    Close = 2


class RenkoBarItem:
    def __init__(self):
        self._timestamp = None
        self._open = None
        self._high = None
        self._low = None
        self._close = None

    def set(self, timestamp_value, open_price, close_price):
        self._timestamp = timestamp_value
        self._open = open_price
        self._close = close_price

    @property
    def is_bullish_bar(self):
        return self._close > self._open

    @property
    def is_bearish_bar(self):
        return self._close < self._open

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def open(self):
        return self._open

    @property
    def close(self):
        return self._close


class RenkoBars(LookBehindPool):
    def __init__(self, capacity):
        super().__init__(capacity, lambda: RenkoBarItem())
        self.technicals = Technicals(lambda: self.current)

    def register(self, ta_function, value_item_lambda):
        self.technicals.register(ta_function, value_item_lambda)

    def write(self, timestamp_value, open_price, close_price):
        self.set_forward(lambda item: item.set(timestamp_value, open_price, close_price))

        for technical in self.technicals:
            technical.ta_function.calculate(timestamp_value, technical.value_item_lambda(technical.price_bar_lambda()))


class Renko(PriceAction):
    def __init__(self, feed_interval, pip_factor, on_price_action=None, capacity=100):
        super().__init__(PriceChartType.Renko, RenkoAggregator(feed_interval, pip_factor), RenkoBars(capacity))
        self._on_price_action = on_price_action
        self._initialized = False
        self.technicals = self._price_bars.technicals

    def price_action(self, timestamp_value, bid, ask):
        last_price_bar_sequence = self._price_bars.sequence
        if self._initialized:
            self._aggregator.price_action(timestamp_value, bid, ask, self._price_bars)
        else:
            self._aggregator.initialize(bid, ask)
            self._initialized = True
        if self._on_price_action is not None and self._price_bars.sequence > last_price_bar_sequence:
            for i in range(self._price_bars.sequence-last_price_bar_sequence):
                self._on_price_action(self._price_bars[i], self._price_bars)

    def back_fill(self, timestamp_value, open_price, close_price):
        self._price_bars.write(timestamp_value, open_price, close_price)


class RenkoAggregator:
    def __init__(self, range_unit, pip_factor):
        self._range = range_unit.interval
        self._pipFactor = pip_factor
        self._previous_open = None

    def initialize(self, bid, ask):
        #current_price = (bid + ask) / 2
        current_price = bid
        self._previous_open = current_price

    def price_action(self, timestamp_value, bid, ask, renko_bars):
        #current_price = (bid + ask) / 2
        current_price = bid
        pips_difference = (current_price - self._previous_open) * self._pipFactor

        if pips_difference > 0:
            if pips_difference >= self._range.units:
                pips_remaining = pips_difference
                pip_range = (1/self._pipFactor) * self._range.units
                adj_microsecond= timestamp_value.microsecond
                while pips_remaining >= self._range.units:
                    closing_price = self._previous_open + pip_range
                    bar_timestamp = Timestamp(timestamp_value.year, timestamp_value.month, timestamp_value.day,
                                              timestamp_value.hour, timestamp_value.minute, timestamp_value.second,
                                              adj_microsecond)
                    renko_bars.write(bar_timestamp, self._previous_open, closing_price)
                    adj_microsecond += 1
                    self._previous_open = closing_price
                    pips_remaining -= self._range.units

        if pips_difference < 0:
            if -pips_difference >= self._range.units:
                pips_remaining = pips_difference
                pip_range = (1/self._pipFactor) * self._range.units
                adj_microsecond = timestamp_value.microsecond
                while -pips_remaining >= self._range.units:
                    closing_price = self._previous_open - pip_range
                    bar_timestamp = Timestamp(timestamp_value.year, timestamp_value.month, timestamp_value.day,
                                              timestamp_value.hour, timestamp_value.minute, timestamp_value.second,
                                              adj_microsecond)
                    renko_bars.write(bar_timestamp, self._previous_open, closing_price)
                    adj_microsecond += 1
                    self._previous_open = closing_price
                    pips_remaining += self._range.units


class RenkoFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('renko', BinaryFileHeaderFormat('iiiff'))


class RenkoFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, RenkoFileInfo())

    def append(self, timestamp_value, open_price, close_price):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.header_format.format, date_time_split[0], date_time_split[1],
                               date_time_split[2], open_price, close_price)
        self._append(row_data)


RenkoFileRecord = namedtuple("RenkoFileRecord", "timestamp open close")


class RenkoFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, RenkoFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return RenkoFileRecord(TimestampConverter.from_tick_split(data[0], data[1], data[2]), data[3], data[4])

    def read_all(self):
        if not self._file_context._is_file_open:
            raise Exception("File is not open.")
        result = self.read()
        while result is not None:
            yield result
            result = self.read()


class RenkoPublisher:
    def __init__(self, on_price_action=None):
        self._on_price_action = on_price_action
        self._price_feeds = {}
        self._price_bars = {}
        self._ticker_references = []

    def setup(self, ticker_reference):
        self._ticker_references.append(ticker_reference)

        price_bar = RenkoBars(100)
        self._price_bars[ticker_reference.id] = price_bar

        aggregator = Renko(ticker_reference.interval, ticker_reference.symbol.pip_factor,
                           lambda current_price, price_history: self.price_action(ticker_reference, current_price,
                                                                                  price_history))
        self._price_feeds[ticker_reference.id] = aggregator

        return price_bar

    def price_action(self, ticker_reference, current_price, price_history):
        self._price_bars[ticker_reference.id].write(current_price.timestamp, current_price.open, current_price.close)
        if self._on_price_action is not None:
            self._on_price_action(ticker_reference, current_price, price_history)

    @property
    def price_bars(self):
        return self._price_bars

    @property
    def price_feeds(self):
        return self._price_feeds

    @property
    def ticker_references(self):
        return self._ticker_references
