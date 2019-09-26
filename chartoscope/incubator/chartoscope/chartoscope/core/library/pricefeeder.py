from chartoscope.core.library import *

class PriceFeeder(Feeder):
    def __init__(self):
        super().__init__()

    @staticmethod
    def start(subscriber):
        app_type = subscriber.__class__.__bases__[0]
        if app_type is PriceAction:
            if subscriber.price_bar_type == PriceChartType.Ohlc:
                initialized = False
                next_minute = datetime.datetime(2017, 1, 1, 0, 0)
                for x in range(1000000):
                    next_minute = next_minute + datetime.timedelta(minutes=1)
                    if initialized:
                        subscriber.aggregator.price_action(Timestamp(datetime_value=next_minute), x, x + 2,
                                                           subscriber.price_bars)
                    else:
                        subscriber.aggregator.initialize(Timestamp(datetime_value=next_minute), x, x + 2)
                        initialized = True
