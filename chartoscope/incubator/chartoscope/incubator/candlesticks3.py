#!/usr/bin/env python
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter, WeekdayLocator,\
    DayLocator, MONDAY
from mpl_finance import *

from chartoscope.core.common import *
from chartoscope.core.library import *

import numpy as np
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


tz = get_localzone()
ohlc = []
strconverter = mdates.strpdate2num('%Y%m%d %H:%M')
timeFrame= TimeframeInterval.M30

reader = HeikenAshiFileReader('EURUSD_2013_04_M30.heikenashi')
reader.open()
result= reader.read()
counter= 0
while result!=None:
    dt = result[0].to_datetime()
    strdt = dt.astimezone(tz).strftime('%Y%m%d %H:%M')
    append_me = strconverter(strdt), result[1], result[2], result[3], result[4]
    ohlc.append(append_me)
    counter += 1
    sys.stdout.write('\r{0} processed'.format(counter))
    sys.stdout.flush()
    result = reader.read()

reader.close()

fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)

def weekday_candlestick(ohlc_data, ax, fmt='%b %d', freq=7, **kwargs):
    """ Wrapper function for matplotlib.finance.candlestick_ohlc
        that artificially spaces data to avoid gaps from weekends """

    # Convert data to numpy array
    ohlc_data_arr = np.array(ohlc_data)
    ohlc_data_arr2 = np.hstack(
        [np.arange(ohlc_data_arr[:,0].size)[:,np.newaxis], ohlc_data_arr[:,1:]])
    ndays = ohlc_data_arr2[:,0]  # array([0, 1, 2, ... n-2, n-1, n])

    # Convert matplotlib date numbers to strings based on `fmt`
    dates = mdates.num2date(ohlc_data_arr[:,0])
    date_strings = []
    for date in dates:
        date_strings.append(date.strftime(fmt))

    # Plot candlestick chart
    candlestick_ohlc(ax, ohlc_data_arr2, **kwargs)

    # Format x axis
    ax.set_xticks(ndays[::freq])
    ax.set_xticklabels(date_strings[::freq], rotation=45, ha='right')
    ax.set_xlim(ndays.min(), ndays.max())

    plt.show()

weekday_candlestick(ohlc, ax=ax, fmt='%b %d', freq=3, width=0.5)