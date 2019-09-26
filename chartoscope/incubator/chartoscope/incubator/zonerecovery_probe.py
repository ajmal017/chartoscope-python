from chartoscope.core.common import *
from chartoscope.core.library import *
from chartoscope.resonator import Backtest
from incubator.acme import *


class ZoneRecoveryProbe(Probe):
    def __init__(self, ticker_symbol, data_feed, on_entry=None, on_exit=None):
        super().__init__(data_feed)
        self._on_entry = on_entry
        self._on_exit = on_exit
        self._ticker_symbol = ticker_symbol
        self._long_term_trend_ticker = None
        self._long_term_trend_feed = None
        self._long_term_atr = None
        self._mid_term_trend_ticker = None

        self._long_term_market_view = MarketView.Neutral
        self._mid_term_market_view = MarketView.Neutral
        self._short_term_market_view = MarketView.Neutral

        self._previous_long_term_market_view = MarketView.Neutral
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
        self.upper_zone_level = None
        self.lower_zone_level = None
        self.is_zone_recovery_mode= False
        self.is_zone_hedging_mode= False

    def start(self, long_term_trend_timeframe=TimeframeInterval.H4, long_term_trend_atr_period=14,
              mid_term_trend_timeframe=TimeframeInterval.M30, mid_term_ema_period=20,
              short_term_trend_range=RangeInterval.R10, short_term_trend_macd_periods=MacdCalculationResult(21, 12, 5)
              ):
        self._long_term_trend_ticker = TickerReference(self._ticker_symbol, FeedInterval(long_term_trend_timeframe))

        self._long_term_atr = AtrIndicator(long_term_trend_atr_period)
        self._long_term_trend_feed = self.data_feed.heiken_ashi.setup(self._long_term_trend_ticker)
        self._long_term_trend_feed.register(self._long_term_atr, lambda heiken_ashi_bar: heiken_ashi_bar)

        self._mid_term_trend_ticker = TickerReference(self._ticker_symbol, FeedInterval(mid_term_trend_timeframe))
        self._mid_term_trend_feed = self.data_feed.heiken_ashi.setup(self._mid_term_trend_ticker)
        self._mid_term_ema = EmaIndicator(mid_term_ema_period)
        self._mid_term_trend_feed.register(self._mid_term_ema, lambda heiken_ashi_bar: heiken_ashi_bar.close)

        self._short_term_trend_ticker = TickerReference(self._ticker_symbol, FeedInterval(short_term_trend_range))
        self._short_term_trend_feed = self.data_feed.renko.setup(self._short_term_trend_ticker, )
        self._short_term_trend_macd = MacdIndicator(short_term_trend_macd_periods.slow_ema,
                                                    short_term_trend_macd_periods.fast_ema,
                                                    short_term_trend_macd_periods.signal_ema)
        self._short_term_trend_feed.register(self._short_term_trend_macd, lambda renko_bar: renko_bar.close, )

    def entry_setup(self):
        if self._long_term_market_view != MarketView.Neutral and \
                self._long_term_market_view == self._mid_term_market_view and \
                self._mid_term_market_view == self._short_term_market_view\
                and self._long_term_atr.has_value:

            return MarketPosition.inverse(MarketPosition.from_market_view(self._short_term_market_view))
            #return MarketPosition.from_market_view(self._short_term_market_view)
        else:
            return MarketPosition.NoPosition

    def on_entry(self, position):
        self.market_position = position.market_position

        self._last_short_term_market_view = self._short_term_market_view
        self._last_mid_term_market_view= self._mid_term_market_view

        if position.market_position==MarketPosition.Long:
            self.profit_target= position.entry_price + (self._long_term_atr.current.value / 2)
            self.upper_zone_level = position.entry_price - ((1/10000) * 10)
            self.lower_zone_level = position.entry_price - ((1/10000) * 10)
        elif position.market_position==MarketPosition.Short:
            self.profit_target= position.entry_price - (self._long_term_atr.current.value / 2)
            self.upper_zone_level = position.entry_price + ((1/10000) * 10)
            self.lower_zone_level = position.entry_price + ((1/10000) * 10)


        if self._on_entry is not None:
            self._on_entry(self.market_position, self.entry_price)

    def get_exit_price(self, entry_position):
        if entry_position.market_position==MarketPosition.Long:
            return self._bid
        elif entry_position.market_position==MarketPosition.Short:
            return self._ask
        else:
            return None

    def can_exit_position(self, entry_position):
        if self.is_zone_recovery_mode:
            is_profit_target_reached = False

            if entry_position.market_position == MarketPosition.Long:
                is_profit_target_reached = self.profit_target is not None and self._bid >= self.profit_target
            elif entry_position.market_position == MarketPosition.Short:
                is_profit_target_reached = self.profit_target is not None and self._ask <= self.profit_target

            if is_profit_target_reached:
                print("Profit target reached!")
                return True
            elif self.is_zone_hedging_mode:
                exit_price = self.get_exit_price(entry_position)
                if entry_position.market_position == MarketPosition.Long and exit_price < self.upper_zone_level:
                    print("Zone recovery re-entry!")
                    self.is_zone_hedging_mode = False
                elif entry_position.market_position == MarketPosition.Short and exit_price > self.lower_zone_level:
                    print("Zone recovery re-entry!")
                    self.is_zone_hedging_mode= False
                return False
            else:
                exit_price = self.get_exit_price(entry_position)
                if entry_position.market_position == MarketPosition.Long and exit_price <= self.lower_zone_level:
                    print("Hedging position")
                    position = self.enter_position(self._bid, self._ask, MarketPosition.Short)
                    self.profit_target= self.profit_target= position.entry_price - (self._long_term_atr.current.value / 2)
                    self.is_zone_hedging_mode = True
                elif entry_position.market_position == MarketPosition.Short and exit_price >= self.upper_zone_level:
                    print("Hedging position")
                    position = self.enter_position(self._bid, self._ask, MarketPosition.Long)
                    self.profit_target = self.profit_target= position.entry_price + (self._long_term_atr.current.value / 2)
                    self.is_zone_hedging_mode = True

                return False
        else:
            is_winning= True

            is_profit_target_reached = False
            if entry_position.market_position==MarketPosition.Long:
                is_profit_target_reached= self.profit_target is not None and self._bid >= self.profit_target
            elif entry_position.market_position==MarketPosition.Short:
                is_profit_target_reached = self.profit_target is not None and self._ask <= self.profit_target

            if is_profit_target_reached and (self._short_term_market_view != self._last_short_term_market_view):
                print("Profit target reached!")
                return True
            elif (self._short_term_market_view != self._last_short_term_market_view):
                return True
            else:
                exit_price= self.get_exit_price(entry_position)
                if entry_position.market_position==MarketPosition.Long and exit_price < self.upper_zone_level:
                    return True
                    #print("Entering zone recovery level!")
                    #self.is_zone_recovery_mode = True
                elif entry_position.market_position == MarketPosition.Short and exit_price > self.lower_zone_level:
                    #print("Entering zone recovery level!")
                    return True
                    #self.is_zone_recovery_mode = True
                return False

        #return (self._short_term_market_view != self._last_short_term_market_view)
        #return self.stop_loss_hit(entry_position) or (self._mid_term_market_view != self._last_mid_term_market_view and self._short_term_market_view != self._last_short_term_market_view)

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
        if self.market_position == MarketPosition.Long:
            exit_price = self._bid
        elif self.market_position == MarketPosition.Short:
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
            print("Closing Long Position at {0}.  P/L= {1} pips".format(exit_price, profit_loss))
        elif entry_position.market_position==MarketPosition.Short:
            profit_loss = (entry_position.entry_price - exit_price) * 10000
            self.total_profit_loss += profit_loss

            if profit_loss > 0:
                self.total_win += 1
            elif profit_loss < 0:
                self.total_lose += 1
            else:
                self.total_break_even += 1
            print("Closing Short Position at {0} P/L= {1} pips".format(exit_price, profit_loss))

        if self._on_exit is not None:
            self._on_exit(self.market_position, exit_price)

    def on_price_action(self, ticker_reference_id, price_bars):
        if ticker_reference_id == self._long_term_trend_ticker.id:
            if price_bars.current.is_bullish_candle:
                self._long_term_market_view = MarketView.Bullish
            elif price_bars.current.is_bearish_candle:
                self._long_term_market_view = MarketView.Bearish
            else:
                self._long_term_market_view = MarketView.Neutral

            if self._previous_long_term_market_view != self._long_term_market_view:
                self._previous_long_term_market_view = self._long_term_market_view.name

        elif ticker_reference_id == self._mid_term_trend_ticker.id:
            if price_bars.current.is_bullish_candle and self._mid_term_ema.has_value and self._mid_term_ema.current.value < price_bars.current.close:
                self._mid_term_market_view = MarketView.Bullish
            elif price_bars.current.is_bearish_candle and self._mid_term_ema.has_value and self._mid_term_ema.current.value < price_bars.current.close:
                self._mid_term_market_view = MarketView.Bearish
            else:
                self._mid_term_market_view = MarketView.Neutral
        elif ticker_reference_id == self._short_term_trend_ticker.id:
            if price_bars.current.is_bullish_bar and self._short_term_trend_macd.has_value and self._short_term_trend_macd.is_bullish_crossing:
                self._short_term_market_view = MarketView.Bullish
            elif price_bars.current.is_bearish_bar and self._short_term_trend_macd.has_value and self._short_term_trend_macd.is_bearish_crossing:
                self._short_term_market_view = MarketView.Bearish
            else:
                self._short_term_market_view = MarketView.Neutral

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