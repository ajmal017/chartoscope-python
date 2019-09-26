from chartoscope.core.utility.backtestfile import *
from tqdm import tqdm
import time


class SignalSandbox:
    def __init__(self):
        self._rolling_profit_loss = 0

    def on_initialize(self, init_timestamp):
        pass

    def can_open_position(self):
        return True

    def long_entry_setup(self):
        return False

    def short_entry_setup(self):
        return False

    def on_long_entry(self):
        pass

    def on_short_entry(self):
        pass

    def can_exit_short(self):
        return False

    def can_exit_long(self):
        return False

    def on_short_exit(self):
        pass

    def on_long_exit(self):
        pass

    def on_price_action(self, probe_info):
        pass

class BacktestSignalSandbox:
    def __init__(self, probe_reader, signal_sandbox):
        self._probe_reader = probe_reader
        self._signal_sandbox = signal_sandbox
        self._back_test_writer = BacktestFileAppender(".".join((probe_reader._file_name,"signal")))

    def execute(self):
        self._back_test_writer.open()
        signal = self._signal_sandbox
        has_position = False
        active_position = MarketPosition.NoPosition
        long_position_count = 0
        short_position_count = 0
        entry_price = None
        initialized = False
        #for row in tqdm(self._probe_reader.read_all(), total=self._probe_reader._file_info.row_count) :
        for row in self._probe_reader.read_all():
            if not initialized:
                signal.on_initialize(row["timestamp"])
                initialized = True

            signal.on_price_action(row)
            if has_position:
                if active_position == MarketPosition.Long:
                    if signal.can_exit_long():
                        exit_price = row["close"]  - (1/15000)
                        signal.on_long_exit()
                        self._back_test_writer.append(row["timestamp"], entry_price, active_position.value, exit_price)
                        has_position = False
                        active_position = MarketPosition.NoPosition
                        signal._rolling_profit_loss += exit_price - entry_price
                elif active_position == MarketPosition.Short:
                    if signal.can_exit_short():
                        exit_price = row["close"]
                        signal.on_short_exit()
                        self._back_test_writer.append(row["timestamp"], entry_price, active_position.value, exit_price)
                        has_position = False
                        active_position = MarketPosition.NoPosition
            else:
                if signal.can_open_position():
                    if signal.long_entry_setup():
                        entry_position = MarketPosition.Long
                    elif signal.short_entry_setup():
                        entry_position = MarketPosition.Short
                    else:
                        entry_position = MarketPosition.NoPosition

                    if entry_position == MarketPosition.Long:
                        entry_price = row["close"]
                        signal.on_long_entry()
                        has_position = True
                        active_position = entry_position
                        long_position_count += 1
                    elif entry_position == MarketPosition.Short:
                        entry_price = row["close"]  - (1/15000)
                        signal.on_short_entry()
                        active_position = entry_position
                        has_position = True
                        short_position_count += 1

        self._back_test_writer.close()
