class TickerReference:
    LastTickerId = 0

    def __init__(self, symbol, interval):
        self._symbol = symbol
        self._interval = interval
        TickerReference.LastTickerId += 1
        self._id = TickerReference.LastTickerId

    @property
    def interval(self):
        return self._interval

    @property
    def symbol(self):
        return self._symbol

    @property
    def id(self):
        return self._id

class TickerSymbol:
    def __init__(self, symbol, pip_factor=1):
        self._symbol = symbol
        self._pip_factor = pip_factor

    @property
    def pip_factor(self):
        return self._pip_factor
