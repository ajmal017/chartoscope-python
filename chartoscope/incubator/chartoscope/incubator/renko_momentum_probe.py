from chartoscope.core.common import *
from chartoscope.core.library import *
from chartoscope.resonator import Backtest
from incubator.acme import *


class RenkoMomentumProbe(Probe):
    def __init__(self, ticker_symbol, data_feed, on_entry=None, on_exit=None):
        super().__init__(data_feed)
        self._on_entry = on_entry
        self._on_exit = on_exit
        self._ticker_symbol = ticker_symbol

        self.market_position = MarketPosition.NoPosition
        self.entry_price = None
        self.total_profit_loss = 0
        self.total_win = 0
        self.total_lose = 0
        self.total_break_even = 0
        self.current_ask_price= None
        self.current_bid_price = None
        self.last_higher_high = None
        self.last_lower_low = None
        self.profit_target= None
        self.price_action_time = None
        self.market_view = None
        self.rate_of_change = None
        self.has_reversed = False

    def start(self, renko_range=RangeInterval.R1, slow_hma=14, fast_hma=200):
        self._ticker_reference = TickerReference(self._ticker_symbol, FeedInterval(renko_range))
        self._renko_feed = self.data_feed.renko.setup(self._ticker_reference)

        self._fast_hma = HmaIndicator(fast_hma, 1000)
        #self._rsi = RsiIndicator(14)
        #self._macd = MacdIndicator(26, 12, 9)
        self._renko_feed.register(self._fast_hma, lambda renko_bar: renko_bar.close)
        #self._renko_feed.register(self._rsi, lambda renko_bar: renko_bar.close)
        #self._renko_feed.register(self._macd, lambda renko_bar: renko_bar.close)

    def entry_setup(self):
        if self.market_view == MarketView.Bullish and self._fast_hma.rate_of_change > 10:
            self.has_reversed = False
            return MarketPosition.Long
        elif self.market_view == MarketView.Bearish and self._fast_hma.rate_of_change < 10:
            self.has_reversed = False
            return MarketPosition.Short
        else:
            return MarketPosition.NoPosition

    def on_entry(self, position):
        self.market_position = position.market_position
        if position.market_position == MarketPosition.Long:
            print("Opening Long Position with bid price {0} on {1}".format(self._bid, self.price_action_time.to_string("%Y%m%d %H:%M:%S")))
        elif position.market_position == MarketPosition.Short:
            print("Opening Short Position with ask price {0} on {1}".format(self._ask,
                                                                         self.price_action_time.to_string(
                                                                             "%Y%m%d %H:%M:%S")))

    def get_exit_price(self, entry_position):
        if entry_position.market_position==MarketPosition.Long:
            return self._bid
        elif entry_position.market_position==MarketPosition.Short:
            return self._ask
        else:
            return None

    def can_exit_position(self, entry_position):
        return self.has_reversed

    def stop_loss_hit(self, entry_position):
        is_stop_loss= False
        if entry_position.market_position==MarketPosition.Long:
            stop_loss= entry_position.entry_price - ((1 / 10000) * 10) # 10 pips
            is_stop_loss= self._ask < stop_loss
        elif entry_position.market_position==MarketPosition.Short:
            stop_loss = entry_position.entry_price + ((1 / 10000) * 10) # 10 pips
            is_stop_loss = self._bid > stop_loss
        else:
            is_stop_loss = False

        if is_stop_loss:
            print("Stop loss hit!")

        return is_stop_loss

    def on_exit(self, entry_position):

        exit_price = None
        if entry_position.market_position == MarketPosition.Long:
            exit_price = self._bid
        elif entry_position.market_position == MarketPosition.Short:
            exit_price = self._ask

        if entry_position.market_position==MarketPosition.Long:
            profit_loss = (exit_price - entry_position.entry_price) * 10000
            self.total_profit_loss += profit_loss
            if profit_loss > 0:
                self.total_win += 1
            elif profit_loss < 0:
                self.total_lose += 1
            else:
                self.total_break_even += 1
            print("Closing Long Position with bid {0} on {1}  P/L= {2} pips".format(exit_price, self.price_action_time.to_string(
                                                                                  "%Y%m%d %H:%M:%S"), profit_loss))
        elif entry_position.market_position==MarketPosition.Short:
            profit_loss = (entry_position.entry_price - exit_price) * 10000
            self.total_profit_loss += profit_loss

            if profit_loss > 0:
                self.total_win += 1
            elif profit_loss < 0:
                self.total_lose += 1
            else:
                self.total_break_even += 1
            print("Closing Short Position with ask {0} on {1} P/L= {2} pips".format(exit_price, self.price_action_time.to_string(
                                                                                  "%Y%m%d %H:%M:%S"), profit_loss))

        # if self._fast_hma.has_reversed:
        #     if self._fast_hma.is_downward_slope and self._fast_hma.rate_of_change < 10:
        #         self._reentry_position = MarketPosition.Short
        #         print("Opening Short Position with ask price {0} at {1}".format(self._ask,
        #                                                                       self.price_action_time.to_string(
        #                                                                           "%Y%m%d %H:%M:%S")))
        #     elif self._fast_hma.is_upward_slope and self._fast_hma.rate_of_change > 10:
        #         self._reentry_position = MarketPosition.Long
        #         print("Opening Long Position with bid price {0} at {1}".format(self._bid,
        #                                                                      self.price_action_time.to_string(
        #                                                                          "%Y%m%d %H:%M:%S")))
        #     else:
        #         self._reentry_position = MarketPosition.NoPosition
        # else:
        #     self._reentry_position = MarketPosition.NoPosition

        #if self._on_exit is not None:
        #    self._on_exit(self.market_position, exit_price)




    def on_price_action(self, ticker_reference_id, price_bars):
        self.price_action_time = price_bars.current.timestamp

        if self._fast_hma.has_reversed:
            if self._fast_hma.is_downward_slope:
                self.market_view = MarketView.Bearish
            elif self._fast_hma.is_upward_slope:
                self.market_view = MarketView.Bullish
            else:
                self.market_view = MarketView.Neutral
        else:
            self.market_view = MarketView.Neutral

        #print(self._fast_hma.rate_of_change)


    def _on_short_term_price_action(self, renko_price_bars):
        pass

    def can_enter_long(self):
        pass

    def can_enter_short(self):
        pass

    def on_long_entry(self):
        pass

    def on_short_entry(self):
        pass

    def can_exit_long(self):
        pass

    def can_exit_short(self):
        pass

    def on_long_exit(self):
        pass

    def on_short_exit(self):
        pass

    def finalize(self):
        print("Total P/L: {0} pips".format(self.total_profit_loss))
        print("Total Signals: {0}".format(self.total_win + self.total_lose))
        print("Total Win: {0}".format(self.total_win))
        print("Total Lose: {0}".format(self.total_lose))
        print("Total Break-even: {0}".format(self.total_break_even))