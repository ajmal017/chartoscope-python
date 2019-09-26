from chartoscope.core.library import *
from tqdm import  tqdm
class AcmeFeed:
    def __init__(self, start_from=None, days=None):
        pass
        self.ohlc= OhlcPublisher()



class AcmeBroker:
    def __init__(self, dataFeed):
        self.dataFeed= dataFeed

    def getExecutionProfile(self):
        return ExecutionProfile()

class AcmeFeed:
    def __init__(self, data_source=None):
        self._dataSource= data_source
        self.heiken_ashi= HeikenAshiPublisher()
        self.renko= RenkoPublisher()
        self.in_position= False
        self._current_bid = None
        self._current_ask = None

    def pump(self, chartoscope_app=None, backFillInfo=None, start_from=None, days=None):
        if chartoscope_app is None:
            reader = BidAskFileReader(
                r'C:\Users\Ronaldo\PycharmProjects\chartoscope\chartoscope\brokers\acme\EURUSD_2013_04.bidask')
            fileInfo = reader.open()
            has_started = False
            next_day_ticks= start_from.next_day_ticks(start_from.year, start_from.month, start_from.day, days)
            for result in tqdm(reader.read_all(), total=fileInfo.rowCount):
                timestamp= result.timestamp
                if timestamp.ticks >= start_from.ticks and timestamp.ticks<= next_day_ticks:
                    has_started= True
                    self._current_bid = result.bid
                    self._current_ask = result.ask

                    for tickerReference in self.heiken_ashi._tickerReferences:
                        self.heiken_ashi._priceFeeds[tickerReference.id].price_action(result[0], result[1], result[2])

                    for tickerReference in self.renko._tickerReferences:
                        self.renko._aggregators[tickerReference.id].price_action(result[0], result[1], result[2])
                elif has_started:
                    break
        else:
            self._app= chartoscope_app
            reader = BidAskFileReader(r'C:\Users\Ronaldo\PycharmProjects\chartoscope\chartoscope\brokers\acme\EURUSD_2013_04.bidask')
            fileInfo= reader.open()
            requiresBackfill= backFillInfo!=None

            self._app.start()

            for result in tqdm(reader.read_all(), total=fileInfo.rowCount):

                if requiresBackfill:
                    if result.timestamp.ticks<backFillInfo.lastSavePoint.ticks:
                        self._app.back_fill(result)
                    else:
                        requiresBackfill= False
                else:
                    self._current_bid= result.bid
                    self._current_ask= result.ask

                    self._app.bid_ask_update(result.bid, result.ask)

                    if self.in_position:
                        position= self._app.entry_positions[self._app._current_position_id]
                        if self._app.can_exit_position(position):
                            self._app.exit_all_positions()

                    self.in_position = len(self._app.entry_positions) > 0

                    for tickerReference in self.heiken_ashi._tickerReferences:
                        self.heiken_ashi._priceFeeds[tickerReference.id].price_action(result[0], result[1], result[2])

                    for tickerReference in self.renko._tickerReferences:
                        self.renko._aggregators[tickerReference.id].price_action(result[0], result[1], result[2])

            self._app.finalize()

        reader.close()

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