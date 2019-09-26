#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from mpl_finance import *

from chartoscope.core.common import *
from chartoscope.core.library import *


import matplotlib.dates as mdates
from tzlocal import get_localzone
import sys

def bytespdate2num(fmt, encoding='utf-8'):
    strconverter = mdates.strpdate2num(fmt)

    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)

    return bytesconverter

# (Year, month, day) tuples suffice as args for quotes_historical_yahoo
date1 = (2004, 2, 1)
date2 = (2004, 4, 12)


mondays = WeekdayLocator(MONDAY)        # major ticks on the mondays
alldays = DayLocator()              # minor ticks on the days
weekFormatter = DateFormatter('%b %d')  # e.g., Jan 12
dayFormatter = DateFormatter('%d')      # e.g., 12


def updatePrice(ohlc, currentPriceBar, strconverter, tz):
    dt = currentPriceBar.timestamp.to_datetime()
    strdt = dt.astimezone(tz).strftime('%Y%m%d %H:%M')
    append_me = strconverter(strdt), currentPriceBar.open, currentPriceBar.high, currentPriceBar.low, currentPriceBar.close
    ohlc.append(append_me)

tz = get_localzone()
ohlc = []
strconverter = mdates.strpdate2num('%Y%m%d %H:%M')
timeFrame= TimeframeInterval.M10

m10Ohlc= Ohlc(timeFrame, lambda currentPrice, priceHistory: updatePrice(ohlc, currentPrice, strconverter, tz))


reader = BidAskFileReader('EURUSD-2013-04.bidask')
reader.open()
result= reader.read()
counter= 0
while result!=None:
    m10Ohlc.price_action(result[0], result[1], result[2])
    counter += 1
    sys.stdout.write('\r{0} processed'.format(counter))
    sys.stdout.flush()
    result = reader.read()
    if counter > 1000000:
        break


fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

if timeFrame.timeUnit==TimeUnit.Minute:
    for label in ax.xaxis.get_ticklabels():
        label.set_rotation(45)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d %H:%M'))
    #ax.xaxis.set_major_locator(mticker.MaxNLocator(6))
    candlestick_ohlc(ax, ohlc, width=0.001, colorup='#77d879', colordown='#db3f3f')
else:
    ax.xaxis.set_major_locator(mondays)
    ax.xaxis.set_minor_locator(alldays)
    ax.xaxis.set_major_formatter(weekFormatter)
    #ax.xaxis.set_minor_formatter(dayFormatter)
    candlestick_ohlc(ax, ohlc, width=0.6)

#plot_day_summary(ax, quotes, ticksize=3)

#candlestick_ohlc(ax, ohlc, width=0.6)

ax.xaxis_date()
ax.autoscale_view()
plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')

plt.show()