from chartoscope.core.common import TickerReference


class Feeder:
    def __init__(self):
        pass


class TickFeeder:
    def __init__(self, feed_provider):
        self._feed_setup_list = []
        feed_provider.subscribe(self._price_action)

    def setup(self, ticker, interval, price_option):
        self._feed_setup_list.append((ticker, interval, price_option))
        return TickerReference(ticker, interval)

    def _price_action(self, timestamp, bid, ask):
        pass
        # for feedSetup in self._feedSetupList:
        #    feedSetup[2].write(timestamp,1,1,1,(bid + ask)/2)
        #self._ohlc.write(timestamp, 1, 1, 1, (bid + ask) / 2)

    def subscribe(self):
        pass

    def register(self, probe):
        pass

    def back_fill(self):
        pass

    def activate(self):
        pass
