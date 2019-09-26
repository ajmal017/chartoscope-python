import time
import datetime
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from chartoscope.core.library.stock import StockFileReader

mpl.rcParams.update({'font.size': 8})

each_stock_file = 'TSLA_2012_D1.stock', 'AAPL_2012_D1.stock'

def graph_data(stock_file):
    stock = StockFileReader(stock_file)
    stock.open()

    dates = []
    openp = []
    highp= []
    lowp= []
    closep= []
    volume = []

    dateconverter= mdates.strpdate2num("%Y%m%d")
    for row in stock.read_all():
        dates.append(dateconverter(row.timestamp.to_string("%Y%m%d")))
        openp.append(row.open)
        highp.append(row.high)
        lowp.append(row.low)
        closep.append(row.adjusted_close)
        volume.append(row.volume)

    stock.close()

    fig = plt.figure()
    ax1= plt.subplot2grid((5, 4), (0, 0), rowspan=4, colspan=4)
    ax1.plot(dates, openp)
    ax1.plot(dates, highp)
    ax1.plot(dates, lowp)
    ax1.plot(dates, closep)
    plt.ylabel('Stock Price')
    ax1.grid(True)

    ax2 = plt.subplot2grid((5, 4), (4, 0), sharex=ax1, rowspan=1, colspan=4)
    ax2.bar(dates, volume)
    ax2.axes.yaxis.set_ticklabels([])
    plt.ylabel('Volume')
    ax2.grid(True)

    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(90)

    for label in ax2.xaxis.get_ticklabels():
         label.set_rotation(45)

    plt.subplots_adjust(left=.10, bottom=.20, top=.90, wspace=.20, hspace=0)

    plt.xlabel('Date')

    plt.suptitle( stock_file + 'Stock Price')

    plt.setp(ax1.get_xticklabels(), visible=False)

    plt.show()

for stock in each_stock_file:
    graph_data(stock)