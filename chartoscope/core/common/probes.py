from chartoscope.core.common import *


class Probe:
    def __init__(self, data_feed):
        self.data_feed = data_feed
        self._entry_positions = {}
        self._current_position_id = 0
        self._bid = None
        self._ask = None
        self._reentry_position = None

    def enter_position(self, bid, ask, market_position):
        entry_price = None
        if market_position == MarketPosition.Long:
            entry_price = ask
        elif market_position == MarketPosition.Short:
            entry_price = bid

        self._current_position_id += 1
        position = ProbeEntryPosition(self._current_position_id, entry_price, market_position)

        self._entry_positions[self._current_position_id] = position

        return position

    def bid_ask_update(self, bid, ask):
        self._bid = bid
        self._ask = ask

    def exit_position(self, position_id):
        self._entry_positions.pop(position_id)

    def exit_all_positions(self):
        for key, value in self._entry_positions.items():
            self.on_exit(value)

        self._entry_positions.clear()

        if self._reentry_position is not None:
            self.enter_position(self._bid, self._ask, self._reentry_position)
            self._reentry_position = None

    @property
    def entry_positions(self):
        return self._entry_positions

    def on_exit(self, entry_position):
        pass


class ProbeEntryPosition:
    def __init__(self, position_id, entry_price, market_position):
        self._position_id = position_id
        self._entry_price = entry_price
        self._market_position = market_position

    @property
    def position_id(self):
        return self._position_id

    @property
    def entry_price(self):
        return self._entry_price

    @property
    def market_position(self):
        return self._market_position


class Probes:
    def __init__(self, current_item):
        self._probe_list = []
        self._current_item = current_item

    def register(self, probe, value_item):
        self._probe_list.append((probe, self._current_item, value_item))

    @property
    def probes(self):
        return self._probe_list
