from chartoscope.core.library import *
from chartoscope.core.extension import *
from tqdm import  tqdm

class AcmeBroker:
    def __init__(self, dataFeed):
        self.dataFeed= dataFeed

    def getExecutionProfile(self):
        return ExecutionProfile()

class AcmeFeed:
    def __init__(self, dataSource):
        self._dataSource= dataSource
        self.heiken_ashi= None
        self.renko= None
        self.in_position= False
        self._current_bid = None
        self._current_ask = None

    def start(self, chartoscope_app, backFillInfo=None):
        self.heiken_ashi = HeikenAshiPublisher(self.priceAction)
        self.renko = RenkoPublisher(self.priceAction)

        self._app= chartoscope_app
        reader = BidAskFileReader('EURUSD_2013_04.bidask')
        fileInfo= reader.open()
        requiresBackfill= backFillInfo!=None
        self._app.start()

        #for result in tqdm(reader.read_all(), total=fileInfo.row_count):
        for result in reader.read_all():

            if requiresBackfill:
                if result.timestamp.ticks<backFillInfo.lastSavePoint.ticks:
                    self._app.back_fill(result)
                else:
                    requiresBackfill= False
            else:
                self._current_bid= result.bid
                self._current_ask= result.ask

                self._app.bid_ask_update(result.bid, result.ask)

                self.in_position = len(self._app.entry_positions) > 0

                if self.in_position:
                    position= self._app.entry_positions[self._app._current_position_id]
                    if self._app.can_exit_position(position):
                        self._app.exit_all_positions()

                for tickerReference in self.heiken_ashi._ticker_references:
                    self.heiken_ashi._price_feeds[tickerReference.id].price_action(result[0], result[1], result[2])

                for ticker_reference in self.renko.ticker_references:
                    self.renko._price_feeds[ticker_reference.id].price_action(result[0], result[1], result[2])

        reader.close()

        self._app.finalize()

    def priceAction(self, tickerReference, priceBar, priceBars):
        self._app.on_price_action(tickerReference.id, priceBars)

        if not self.in_position:
            entry_position = self._app.entry_setup()
            self.in_position = entry_position != MarketPosition.NoPosition

            if self.in_position:
                position= self._app.enter_position(self._current_bid, self._current_ask, entry_position)
                self._app.on_entry(position)


class ExecutionProfile:
    def __init__(self):
        self._profitAndLoss = [1, 2, 3]