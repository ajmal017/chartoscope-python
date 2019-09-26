from chartoscope.core.library import *

def test_renko():
    tickerReference= TickerReference(TickerSymbol('EURUSD'), FeedInterval(RangeInterval.R10))
    renkoBars= RenkoBars(100)
    aggregator = Renko(tickerReference._interval, 1,
                       lambda currentPrice, priceHistory: renkoBars.write(currentPrice.timestamp, currentPrice.open,
                                                                         currentPrice.close))

    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 1), 1, 1)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 2), 9, 9)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 3), 9, 9)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 4), 10, 10)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 5), 11, 11)
    assert(renkoBars.length==1)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 6), 21, 21)
    assert (renkoBars.length == 2)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 7), 41, 41)
    assert(renkoBars.length == 4)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 8), 31, 31)
    assert (renkoBars.length == 5)
    aggregator.price_action(Timestamp(2017, 1, 1, 0, 0, 9), 1, 1)
    assert (renkoBars.length == 8)