from chartoscope.core.common import *
from chartoscope.core.library import *
from chartoscope.core.extension.probe import *
from chartoscope.resonator import Backtest
from incubator.acme import *


class ZoneRecoveryProbe(Probe):

    def __init__(self, tickerSymbol, on_entry=None, on_exit=None):
        super().__init__()
        self._on_entry = on_entry
        self._on_exit = on_exit
        self._tickerSymbol = tickerSymbol

    def start(self):
        self._longTermTrendTicker = TickerReference(self._tickerSymbol, FeedInterval(TimeframeInterval.H4))
        longTermPriceFeed = self.dataFeed.heikenAshi.subscribe(self._longTermTrendTicker)
        self._longTermATR = AtrIndicator(20)
        longTermPriceFeed.register(self._longTermATR, lambda heikenAshiBar: heikenAshiBar.close)

        self._midTermTrendTicker= TickerReference(self._tickerSymbol, FeedInterval(TimeframeInterval.M30))
        midTermPriceFeed= self.dataFeed.heikenAshi.subscribe(self._midTermTrendTicker)
        self._midTermEMA= EmaIndicator(20)
        midTermPriceFeed.register(self._midTermEMA,lambda heikenAshiBar: heikenAshiBar.close)

        self._shortTermTrendTicker = TickerReference(self._tickerSymbol, FeedInterval(RangeInterval.R10))
        shortTermPriceFeed= self.dataFeed.renko.subscribe(self._shortTermTrendTicker)
        self._shortTermMACD= MacdIndicator(21, 12, 5)
        shortTermPriceFeed.register(self._shortTermMACD, lambda renkoBar: renkoBar.close)

        self._longTermMarketView= MarketView.Neutral
        self._midTermMarketView = MarketView.Neutral
        self._shortTermMarketView = MarketView.Neutral

        self._previousLongTermMarketView= MarketView.Neutral
        self.marketPosition= MarketPosition.NoPosition
        self.entryPrice= None
        self.totalProfitLoss = 0
        self.totalWin= 0
        self.totalLose= 0
        self.totalDraw= 0

    def entrySetup(self, args):
        return (self._longTermMarketView!=MarketView.Neutral) and  self._longTermMarketView==self._midTermMarketView and self._midTermMarketView==self._shortTermMarketView

    def onEntry(self, args):
        if self._shortTermMarketView==MarketView.Bearish:
            self.marketPosition= MarketPosition.Short
        elif self._shortTermMarketView==MarketView.Bullish:
            self.marketPosition= MarketPosition.Long
        else:
            self.marketPosition= MarketPosition.NoPosition

        self._lastShortTermMarketView= self._shortTermMarketView

        if self.marketPosition==MarketPosition.Long:
            self.entryPrice = self.currentAskPrice
            print('Entering Market Long Position...')
        elif self.marketPosition==MarketPosition.Short:
            self.entryPrice = self.currentBidPrice
            print('Entering Market Short Position...')

        if self._on_entry != None:
            self._on_entry(self.marketPosition, self.entryPrice)

    def exitSetup(self, args):
        return self._midTermMarketView != self._lastShortTermMarketView

    # def exitSignal(self, marketPosition, args):
    #     if (self._hedgingMode==None or not self._hedgingMode):
    #         if marketPosition == MarketPosition.Long:
    #             if self._currentPrice >= self._profitTarget:
    #                 if self._lastShortTermMarketView == self._shortTermMarketView:
    #                     self._rideTheTrendMode= True
    #                     self._virtualStopLoss= self._currentPrice - self._pips(10)
    #                 else:
    #                     self._virtualStopLoss = None
    #             elif self._currentPrice < self._lowerBoundRecoveryLevel:
    #                 self._hedgingMode= True
    #                 self._lastHedgePosition = MarketPosition.Short
    #                 self._breakEvenTarget = self._previousLowerLow
    #                 #Hedge/add reverse position
    #         elif marketPosition == MarketPosition.short:
    #             if self._currentPrice <= self._profitTarget:
    #                 if self._lastShortTermMarketView == self._shortTermMarketView:
    #                     self._rideTheTrendMode = True
    #                     self._virtualStopLoss = self._currentPrice + self._pips(10)
    #                 else:
    #                     self._virtualStopLoss = None
    #             elif self._currentPrice > self._upperBoundRecoveryLevel:
    #                 self._hedgingMode = True
    #                 self._lastHedgePosition= MarketPosition.Long
    #                 self._breakEvenTarget= self._previousHigherHigh
    #                 # Hedge/add reverse position
    #         else:
    #             self._virtualStopLoss= None
    #     else:
    #         if self._lastHedgePosition == MarketPosition.Short:
    #             if self._currentPrice > self._upperBoundRecoveryLevel:
    #                 self._lastHedgePosition = MarketPosition.Long
    #                 # Hedge/add reverse position
    #             elif self._currentPrice <=  self._breakEvenTarget:
    #                 pass
    #                 #close all positions except the last
    #                 #ride the trend
    #         elif self._lastHedgePosition == MarketPosition.Long:
    #             if self._currentPrice > self._upperBoundRecoveryLevel:
    #                 self._lastHedgePosition = MarketPosition.Long
    #                 # Hedge/add reverse position
    #             elif self._currentPrice <=  self._breakEvenTarget:
    #                 pass
    #                 #close all positions except the last
    #                 #ride the trend
    #
    #     return  (self._virtualStopLoss==None and self._lastShortTermMarketView != self._shortTermMarketView) or (self._virtualStopLoss!=None and self._currentPrice < self._virtualStopLoss)

    def onExit(self, args):
        exitPrice= args.priceBars.current.close
        if self._lastShortTermMarketView==MarketView.Bullish:
            profitLoss= (exitPrice - self.entryPrice) * 10000
            print("Closing Long Position at {0}.  P/L= {1} pips".format(exitPrice, profitLoss))
            self.totalProfitLoss += profitLoss
            if profitLoss > 0:
                self.totalWin += 1
            else:
                self.totalLose += 1
        elif self._lastShortTermMarketView==MarketView.Bearish:
            profitLoss = (self.entryPrice - exitPrice) * 10000
            self.totalProfitLoss += profitLoss

            if profitLoss > 0:
                self.totalWin += 1
            elif profitLoss < 0:
                self.totalLose += 1
            else:
                self.totalDraw += 1
            print("Closing Short Position at {0} P/L= {1} pips".format(exitPrice, profitLoss))

        if self._on_exit != None:
            self._on_exit(self.marketPosition, exitPrice)


    def onPriceAction(self, args):
        if args.tickerReferenceId==self._longTermTrendTicker.id:
            if args.priceBars.current.isBullishCandle:
                self._longTermMarketView= MarketView.Bullish
            elif args.priceBars.current.isBearishCandle:
                self._longTermMarketView = MarketView.Bearish
            else:
                self._longTermMarketView = MarketView.Neutral

            if self._previousLongTermMarketView != self._longTermMarketView:
                #print("Long term market view is {}".format(self._longTermMarketView.name) )
                self._previousLongTermMarketView= self._longTermMarketView.name

        elif args.tickerReferenceId==self._midTermTrendTicker.id:
            if args.priceBars.current.isBullishCandle and self._midTermEMA.hasValue and self._midTermEMA.current.value<args.priceBars.current.close:
                self._midTermMarketView= MarketView.Bullish
            elif args.priceBars.current.isBearishCandle and self._midTermEMA.hasValue and self._midTermEMA.current.value<args.priceBars.current.close:
                self._midTermMarketView = MarketView.Bearish
            else:
                self._midTermMarketView = MarketView.Neutral
        elif args.tickerReferenceId == self._shortTermTrendTicker.id:
            if args.priceBars.current.is_bullish_bar and self._shortTermMACD.hasValue and self._shortTermMACD.is_bullish_crossing:
                self._shortTermMarketView= MarketView.Bullish
            elif args.priceBars.current.is_bearish_bar and self._shortTermMACD.hasValue and self._shortTermMACD.is_bearish_crossing:
                self._shortTermMarketView = MarketView.Bearish
            else:
                self._shortTermMarketView = MarketView.Neutral

    def finalize(self):
        print("Total P/L: {0} pips".format(self.totalProfitLoss))
        print("Total Signals: {0}".format(self.totalWin + self.totalLose))
        print("Total Win: {0}".format(self.totalWin))
        print("Total Lose: {0}".format(self.totalLose))
        print("Total Draw: {0}".format(self.totalDraw))

class ZoneRecovery(ExpertAdvisor):
    def __init__(self, tickerSymbol, broker):
        ExpertAdvisor.__init__(self, broker)
        self._tickerSymbol = tickerSymbol
        self.currentBidPrice = None
        self.currentAskPrice= None
        self._probe = None
        self._bid_ask = None
        self._market_position= MarketPosition.NoPosition
        self._entryPrice= None

    def probe_entry(self, market_position, entry_price):
        self._market_position = market_position
        self._entry_price= entry_price

    def probe_exit(self, exit_price):
        self._exit_price= exit_price
        self._market_position = MarketPosition.NoPosition

    def start(self):
        self._probe = ZoneRecoveryProbe(self._tickerSymbol)
        self._bid_ask = self.dataFeed.bidask(self._tickerSymbol)
        self._bid_ask.register(self._probe,
                               (lambda market_position, entry_price: self.probe_entry(market_position, entry_price)),
                               (lambda market_position, exit_price: self.probe_exit(exit_price)))

    def entrySetup(self):
        return self._market_position != MarketPosition

    def onEntry(self):
        if self._market_position ==MarketPosition.Long:
            print('Entering Market Long Position...')
        elif self._market_position ==MarketPosition.Short:
            print('Entering Market Short Position...')

    def exitSetup(self):
        return self._market_position == MarketPosition.NoPosition

    def onExit(self):
        exitPrice= self._exit_price

        if self._market_position==MarketPosition.Long:
            profitLoss= (exitPrice - self._entryPrice) * 10000
            print("Closing Long Position at {0}.  P/L= {1} pips".format(exitPrice, profitLoss))
            self.totalProfitLoss += profitLoss
            if profitLoss > 0:
                self.totalWin += 1
            else:
                self.totalLose += 1
        elif self._market_position==MarketPosition.Short:
            profitLoss = (self.entryPrice - exitPrice) * 10000
            self.totalProfitLoss += profitLoss

            if profitLoss > 0:
                self.totalWin += 1
            elif profitLoss < 0:
                self.totalLose += 1
            else:
                self.totalDraw += 1
            print("Closing Short Position at {0} P/L= {1} pips".format(exitPrice, profitLoss))



    def onPriceAction(self, args):
        if args.tickerReferenceId==self._longTermTrendTicker.id:
            if args.priceBars.current.isBullishCandle:
                self._longTermMarketView= MarketView.Bullish
            elif args.priceBars.current.isBearishCandle:
                self._longTermMarketView = MarketView.Bearish
            else:
                self._longTermMarketView = MarketView.Neutral

            if self._previousLongTermMarketView != self._longTermMarketView:
                #print("Long term market view is {}".format(self._longTermMarketView.name) )
                self._previousLongTermMarketView= self._longTermMarketView.name

        elif args.tickerReferenceId==self._midTermTrendTicker.id:
            if args.priceBars.current.isBullishCandle and self._midTermEMA.hasValue and self._midTermEMA.current.value<args.priceBars.current.close:
                self._midTermMarketView= MarketView.Bullish
            elif args.priceBars.current.isBearishCandle and self._midTermEMA.hasValue and self._midTermEMA.current.value<args.priceBars.current.close:
                self._midTermMarketView = MarketView.Bearish
            else:
                self._midTermMarketView = MarketView.Neutral
        elif args.tickerReferenceId == self._shortTermTrendTicker.id:
            if args.priceBars.current.is_bullish_bar and self._shortTermMACD.hasValue and self._shortTermMACD.is_bullish_crossing:
                self._shortTermMarketView= MarketView.Bullish
            elif args.priceBars.current.is_bearish_bar and self._shortTermMACD.hasValue and self._shortTermMACD.is_bearish_crossing:
                self._shortTermMarketView = MarketView.Bearish
            else:
                self._shortTermMarketView = MarketView.Neutral

    def finalize(self):
        print("Total P/L: {0} pips".format(self.totalProfitLoss))
        print("Total Signals: {0}".format(self.totalWin + self.totalLose))
        print("Total Win: {0}".format(self.totalWin))
        print("Total Lose: {0}".format(self.totalLose))
        print("Total Draw: {0}".format(self.totalDraw))
