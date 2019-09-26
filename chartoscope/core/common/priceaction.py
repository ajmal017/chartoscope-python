class PriceAction:
    def __init__(self, price_bar_type, aggregator, price_bars):
        self._price_bar_type = price_bar_type
        self._aggregator = aggregator
        self._price_bars = price_bars
