

class ZoneRecovery(ExpertAdvisor):
    def __init__(self, brokerGateway):
        ExpertAdvisor.__init__(self, brokerGateway)

        ticker = TickerSymbol("EURUSD")
        timeframe = FeedInterval(TimeframeOption.M1)

        provider = brokerGateway.datafeed(ticker, timeframe)

        self._feeder = TickFeeder(provider)
        tickerReference = self._feeder.setup(ticker, timeframe, OHLCPriceOption.All)

        signalAdvisor = SMACrossSignalAdvisor(tickerReference, 10, 20)
        signalAdvisor.subscribe(self._feeder)

    def backfill(self):
        pass

    def newSignal(self):
        pass

    def newPriceAction(self):
        pass

    def newTick(self):
        pass