from chartoscope.core.common import *
from chartoscope.core.library import SmaIndicator
from chartoscope.brokers.acme import AcmeFeed
from chartoscope.core.utility import Multichart
#Step 01: Create Ticker Reference
tickerReference = TickerReference(TickerSymbol("EURUSD"), FeedInterval(TimeframeInterval.M5))

#Step 02: Create Feed
eurusd_feed= AcmeQuoteFeed()

#Step 03: Setup price action
price_action = eurusd_feed.heiken_ashi.setup(tickerReference, pool_size=600)

#Step 04 Register indicator to Price Action
eurusd_feed.pump(start_from= Timestamp(2013, 4, 1), days=1)


Multichart.pump(eurusd_feed)
Backtest.pump(eurusd_feed)
Resonator.pump(eurusd_feed)
#Step 05 Plot
#Multichart.plot(price_action)
plt.plot()