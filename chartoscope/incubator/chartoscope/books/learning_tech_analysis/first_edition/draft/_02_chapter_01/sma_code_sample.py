from chartoscope.core.common import *
from chartoscope.core.library import SmaIndicator
from chartoscope.brokers.acme import AcmeFeed
from chartoscope.core.utility import Multichart
#Step 01: Create Ticker Reference
tickerReference = TickerReference(TickerSymbol("EURUSD"), FeedInterval(TimeframeInterval.M1))

#Step 02: Create Feed
eurusd_feed= AcmeFeed()

#Step 03: Setup price action
price_action = eurusd_feed.heiken_ashi.setup(tickerReference)

#Step 04:  Create Indicator
sma_20_period = SmaIndicator(20)

#Step 05 Register indicator to Price Action
price_action.register(sma_20_period, lambda ohlc_bar: ohlc_bar.close)

#Step 05 Register indicator to Price Action
eurusd_feed.pump(start_from= Timestamp(2017, 3, 3), days=1)

Multichart.plot(sma_20_period)