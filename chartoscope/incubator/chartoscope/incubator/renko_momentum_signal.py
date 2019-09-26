from renkomomentum import RenkoProbeReader
from chartoscope.core.common import MarketPosition, UtcMarketZone, Timestamp
from chartoscope.core.utility import SignalSandbox, BacktestSignalSandbox, BacktestFileReader, BacktestSignalFileStats
from datetime import timedelta

class RenkoMomentumSignal(SignalSandbox):
    def __init__(self):
        super().__init__()
        self.hma_value = None
        self.roc = None
        self.has_reversed = False
        self.target_reversal = None
        self.timestamp = None
        self.market_session_start = None
        self.session_restarted = True

    def on_initialize(self, init_timestamp):
        self.timestamp = init_timestamp
        self.market_session_start = UtcMarketZone.Frankfurt.value.next_opening_session(init_timestamp)
        self.market_session_end = UtcMarketZone.Tokyo.value.next_opening_session(Timestamp(datetime_value=self.market_session_start))

    def on_price_action(self, probe_info):
        self.hma_value = probe_info["hma"]
        self.roc = probe_info["roc"]
        self.has_reversed = probe_info["hma_reversed"]
        self.timestamp = probe_info["timestamp"]

    def can_open_position(self):
        return True
        # is_within_session = self.timestamp.to_datetime() >= self.market_session_start and self.timestamp.to_datetime() < self.market_session_end
        # if (not is_within_session) or (self._rolling_profit_loss < -((1 / 10000) * 1) or self._rolling_profit_loss > ((1 / 10000) * 5)):
        #     if not self.session_restarted:
        #         self.market_session_start = UtcMarketZone.Frankfurt.value.next_opening_session(self.timestamp) + timedelta(days= 1)
        #         self.market_session_end = UtcMarketZone.Tokyo.value.next_opening_session(
        #             Timestamp(datetime_value=self.market_session_start))  + timedelta(days= 1)
        #
        #         self._rolling_profit_loss = 0
        #
        #         self.session_restarted = True
        # else:
        #     self.session_restarted = False

        return is_within_session

    def long_entry_setup(self):
        if self.roc > 100:
            if self.target_reversal is None:
                self.target_reversal = MarketPosition.Short
                return True
            elif self.target_reversal == MarketPosition.Long:
                self.target_reversal = None
                return True
            else:
                return False
        else:
            return False

    def short_entry_setup(self):
        if self.roc < 100:
            if self.target_reversal is None:
                self.target_reversal = MarketPosition.Long
                return True
            elif self.target_reversal == MarketPosition.Short:
                self.target_reversal = None
                return True
            else:
                return False
        else:
            return False

    def can_exit_short(self):
        return self.has_reversed

    def can_exit_long(self):
        return self.has_reversed

probe_reader = RenkoProbeReader('EURUSD_2017_07_R1_RENKO.probe')
with probe_reader.open():
    backtester = BacktestSignalSandbox(probe_reader, RenkoMomentumSignal())
    backtester.execute()

signal_reader = BacktestFileReader('EURUSD_2017_07_R1_RENKO.probe.signal')
with signal_reader.open():
    signals = list(signal_reader.read_all())

signal_stats = BacktestSignalFileStats('EURUSD_2017_07_R1_RENKO.probe.signal')
signal_stats.generate()