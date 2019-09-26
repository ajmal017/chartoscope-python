import time
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from mpl_finance import *

from chartoscope.core.library import StockFileReader
from chartoscope.core.library import SmaIndicator, RsiIndicator, MacdIndicator

mpl.rcParams.update({'font.size': 8})

#each_stock_file = 'TSLA_2012_D1.stock', 'AAPL_2012_D1.stock'
each_stock_file = ['EBAY_2010_D1.stock']

def graph_data(stock_file):
    stock_reader = StockFileReader(stock_file)
    stock_reader.open()

    date_list = []
    dates = []
    openp = []
    highp= []
    lowp= []
    closep= []
    volume = []
    sma1= []
    sma2= []

    sma1_indicator= SmaIndicator(20)
    sma2_indicator = SmaIndicator(200, 200)
    macd_indicator= MacdIndicator(26, 12, 9)
    rsi_indicator= RsiIndicator(14)

    rsi = []
    macd_line = []
    macd_histogram = []
    macd_signal_line = []

    dateconverter= mdates.strpdate2num("%Y%m%d")

    with stock_reader.open():
        for row in stock_reader.read_all():
            dates.append(dateconverter(row.timestamp.to_string("%Y%m%d")))
            date_list.append(row.timestamp.to_datetime())
            openp.append(row.open)
            highp.append(row.high)
            lowp.append(row.low)
            closep.append(row.adjusted_close)
            volume.append(row.volume)
            sma1_value= sma1_indicator.calculate(row.timestamp, row.close)
            if sma1_value is not None:
               sma1.append(sma1_value)

            sma2_value= sma2_indicator.calculate(row.timestamp, row.close)
            if sma2_value is not None:
               sma2.append(sma2_value)

            rsi_value= rsi_indicator.calculate(row.timestamp, row.close)
            if rsi_value is not None:
                rsi.append(rsi_value)

            macd_value= macd_indicator.calculate(row.timestamp, row.close)
            if macd_value is not None:
                macd_line.append(macd_value)
                macd_signal_line.append(macd_indicator.current.signal_line)
                macd_histogram.append(macd_indicator.current.histogram)

    stock_reader.close()


    x = 0
    y= len(dates)
    candles= []
    while x < y:
        append_line = dates[x], openp[x], highp[x], lowp[x], closep[x], volume[x]
        candles.append((append_line))
        x += 1

    fig = plt.figure(facecolor='#07000d')

    ax0 = plt.subplot2grid((6, 4), (0, 0), rowspan=1, colspan=4, facecolor='#07000d')

    ax0.plot(dates[rsi_indicator.period - 1:], rsi)
    ax0.spines['top'].set_color('#5998ff')
    ax0.spines['bottom'].set_color('#5998ff')
    ax0.spines['left'].set_color('#5998ff')
    ax0.spines['right'].set_color('#5998ff')
    ax0.spines['top'].set_color('#5998ff')
    ax0.tick_params(axis='x', colors='w')
    ax0.tick_params(axis='y', colors='w')
    plt.ylabel('RSI', color='w')

    xLength = range(len(dates))  # length of the x-axis used for plotting coordinates (xLength, y)
    candleAr = list(zip(xLength, openp, highp, lowp, closep, volume))  # The data set
    # Formatter Class to eliminate weekend data gaps on chart
    class Jackarow(mdates.DateFormatter):
        def __init__(self, fmt):
            mdates.DateFormatter.__init__(self, fmt)

        def __call__(self, x, pos=0):
            # This gets called even when out of bounds, so IndexError must be prevented.
            if x < 0:
                x = 0
            elif x >= len(dates):
                x = -1
            return mdates.DateFormatter.__call__(self, dates[int(x)], pos)

    ax1= plt.subplot2grid((6, 4), (1, 0), rowspan=4, colspan=4, facecolor='#07000d')

    print(candles)
    print(candleAr)
    candlestick_ohlc(ax1, candleAr, width=0.75, colorup='#9eff15', colordown='#ff1717', alpha=0.75)

    ax1.plot(xLength[sma1_indicator.period-1:], sma1, label=sma1_indicator.label)
    ax1.plot(xLength[sma2_indicator.period-1:], sma2, label=sma2_indicator.label)

    #ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(30))
    ax1.xaxis.set_major_formatter(Jackarow('%Y%m%d'))
    #ax1.yaxis.label.set_color('w')
    ax1.spines['top'].set_color('#5998ff')
    ax1.spines['bottom'].set_color('#5998ff')
    ax1.spines['left'].set_color('#5998ff')
    ax1.spines['right'].set_color('#5998ff')
    ax1.spines['top'].set_color('#5998ff')
    ax1.tick_params(axis='y', colors='w')
    ax1.tick_params(axis='x', colors='w')

    plt.ylabel('Stock price', color='w')
    plt.legend(loc=3, prop={'size':7}, fancybox=True, borderaxespad=0)
    '''
    ax2 = plt.subplot2grid((5, 4), (4, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    ax2.plot(dates, volume, '#00ffe8', linewidth=.8)
    ax2.fill_between(dates, 0, volume, facecolor='#00ffe8', alpha=.5)
    ax2.axes.yaxis.set_ticklabels([])
    ax2.spines['top'].set_color('#5998ff')
    ax2.spines['bottom'].set_color('#5998ff')
    ax2.spines['left'].set_color('#5998ff')
    ax2.spines['right'].set_color('#5998ff')
    ax2.spines['top'].set_color('#5998ff')
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.ylabel('Volume', color='w')
    '''

    ax1v = ax1.twinx()
    ax1v.fill_between(xLength, 0, volume, facecolor='#00ffe8', alpha=.5)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.spines['top'].set_color('#5998ff')
    ax1v.spines['bottom'].set_color('#5998ff')
    ax1v.spines['left'].set_color('#5998ff')
    ax1v.spines['right'].set_color('#5998ff')
    ax1v.spines['top'].set_color('#5998ff')
    ax1v.set_ylim(0, 2 * max(volume))
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    ax2 = plt.subplot2grid((6, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')

    ax2.plot(xLength[macd_indicator.slow_moving_period + macd_indicator.signal_line_period-2:], macd_line)
    ax2.plot(xLength[macd_indicator.slow_moving_period + macd_indicator.signal_line_period-2:], macd_signal_line)

    fillcolor = '#00ffe8'

    ax2.fill_between(xLength[macd_indicator.slow_moving_period + macd_indicator.signal_line_period-2:], macd_histogram, facecolor=fillcolor, edgecolor=fillcolor, alpha=.5)

    ax2.spines['top'].set_color('#5998ff')
    ax2.spines['bottom'].set_color('#5998ff')
    ax2.spines['left'].set_color('#5998ff')
    ax2.spines['right'].set_color('#5998ff')
    ax2.spines['top'].set_color('#5998ff')
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')
    plt.ylabel('MACD', color='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))

    for label in ax2.xaxis.get_ticklabels():
        label.set_rotation(45)

    plt.subplots_adjust(left=.10, bottom=.20, top=.90, wspace=.20, hspace=0)

    plt.xlabel('Date', color='w')

    plt.suptitle( stock_file + 'Stock Price', color='w')

    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.show()

for stock in each_stock_file:
    graph_data(stock)