# Visualize my stock data

import numpy as np
import time
import datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib.finance import _candlestick
import matplotlib.animation as animation
import matplotlib
import pylab
from urllib.request import urlopen
matplotlib.rcParams.update({'font.size': 9})


def rsiFunc(prices, n=14):
    deltas = np.diff(prices)
    seed = deltas[:n+1]
    up = seed[seed>=0].sum()/n
    down = -seed[seed<0].sum()/n
    rs = up/down
    rsi = np.zeros_like(prices)
    rsi[:n] = 100. - 100./(1.+rs)

    for i in range(n, len(prices)):
        delta = deltas[i-1]
        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta
        up = (up*(n-1)+upval)/n
        down = (down*(n-1)+downval)/n
        rs = up/down
        rsi[i] = 100. - 100./(1.+rs)
    return rsi

def movingAverage(values, window):
    weights = np.repeat(1.0, window)/window
    smas = np.convolve(values, weights, 'valid')
    return smas

def ExpMovingAverage(values, window):
    weights = np.exp(np.linspace(-1, 0, window))
    weights /= weights.sum()
    a = np.convolve(values, weights, mode='full')[:len(values)]
    a[:window] = a[window]
    return a

def computeMACD(x, slow=26, fast=12):
    '''
    macd = 12ema - 26ema
    signal line = 9ema of the macd line
    histogram = macd line - signal line
    '''
    emaSlow = ExpMovingAverage(x, slow)
    emaFast = ExpMovingAverage(x, fast)
    return emaSlow, emaFast, emaFast-emaSlow


def graphData(stock, MA1, MA2):
    fig.clf()
    try:
        try:
            print('Pulling data on', stock)
            urlToVisit = 'http://chartapi.finance.yahoo.com/instrument/1.0/'+stock+'/chartdata;type=quote;range=3d/csv'
            stockFile = []
            try:
                sourceCode = urlopen(urlToVisit).read().decode('utf-8')
                splitSource = sourceCode.split('\n')
                for eachLine in splitSource:
                    splitLine = eachLine.split(',')

                    fixMe = splitLine[0]            #fix Unix timestamp

                    if len(splitLine)==6:
                        if 'values' not in eachLine:
                            fixed = eachLine.replace(fixMe, str(datetime.datetime.fromtimestamp(int(fixMe)).strftime('%Y-%m-%d %H:%M:%S')))
                            stockFile.append(fixed)
            except Exception as e:
                print(str(e), 'failed to organize pulled data')

        except Exception as e:
            print(str(e), 'failed to pull price data')

        date, closep, highp, lowp, openp, volume = np.loadtxt(stockFile, delimiter=',',unpack=True,
                                                              converters={ 0: mdates.bytespdate2num('%Y-%m-%d %H:%M:%S')})

        xLength = range(len(date))          # length of the x-axis used for plotting coordinates (xLength, y)
        SP = len(date[MA2-1:])              # Right hand stopping point so MAs align with CandleStix
        candleAr = list(zip(xLength,openp,closep,highp,lowp,volume)) # The data set


        # Formatter Class to eliminate weekend data gaps on chart
        class Jackarow(mdates.DateFormatter):
            def __init__(self, fmt):
                mdates.DateFormatter.__init__(self, fmt)
            def __call__(self, x, pos=0):
                # This gets called even when out of bounds, so IndexError must be prevented.
                if x < 0:
                    x = 0
                elif x >= len(date):
                    x = -1
                return mdates.DateFormatter.__call__(self, date[int(x)], pos)



# The CANDLESTICK plot
        ax1 = plt.subplot2grid((6, 4), (1,0), rowspan=4, colspan=4, axisbg='#07000D')
        _candlestick(ax1, candleAr[-SP:], width=.75, colorup='#53c156', colordown='#ff1717')

        # Format Colors, Axis, and the like
        ax1.grid(True, color='w')
        ax1.yaxis.label.set_color('w')

        # My Broken Pruner
        ax1.yaxis.set_major_locator(mticker.MaxNLocator(prune='both'))

        ax1.xaxis.set_major_locator(mticker.MaxNLocator(30))
        ax1.xaxis.set_major_formatter(Jackarow('%a %H:%M'))
        ax1.spines['bottom'].set_color("#5998ff")
        ax1.spines['top'].set_color("#5998ff")
        ax1.spines['left'].set_color("#5998ff")
        ax1.spines['right'].set_color("#5998ff")
        ax1.tick_params(axis='y', colors='w')
        ax1.tick_params(axis='x', colors='w')

        plt.ylabel('Stock Price')


    # Create Legend Labels
        label3 = '8 EMA'
        label1 = str(MA1)+ ' SMA'
        label2 = str(MA2)+ ' SMA'


# Plot Moving Averages
        Av1 = movingAverage(closep, MA1)
        Av2 = movingAverage(closep, MA2)
        Ema1 = ExpMovingAverage(closep, 8)


        ax1.plot(xLength[-SP:], Ema1[-SP:],'#5998ff', label=label3, linewidth=1.5)
        ax1.plot(xLength[-SP:], Av1[-SP:], '#fa32e3', label=label1, linewidth=1.5)
        ax1.plot(xLength[-SP:], Av2[-SP:], '#e1edf9', label=label2, linewidth=1.5)





    # Create Legend
        maLeg = plt.legend(loc=2, prop={'size':7}, fancybox=True,)
        maLeg.get_frame().set_alpha(0.4)
        textEd = pylab.gca().get_legend().get_texts()
        pylab.setp(textEd[0:5], color = 'w')


# Volume Overlay
        volumeMin = 0
        ax1v = ax1.twinx()
        ax1v.fill_between(xLength[-SP:], volumeMin, volume[-SP:], facecolor='#00ffe8', alpha=.5)
        ax1v.axes.yaxis.set_ticklabels([])
        ax1v.grid(False)
        ax1v.spines['bottom'].set_color("#5998ff")
        ax1v.spines['top' ].set_color("#5998ff")
        ax1v.spines['left'].set_color("#5998ff")
        ax1v.spines['right'].set_color("#5998ff")
        ax1v.set_ylim(0, 3*volume.max()) # limit height of volume overlay to prevent overlap with candlestix
        ax1v.tick_params(axis='x', colors='w')
        ax1v.tick_params(axis='y', colors='w')


# MACD plot
        ax2 = plt.subplot2grid((6,4), (5,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        fillcolor = '#00ffe8'
        nslow = 26
        nfast = 12
        nema = 9

        emaslow, emafast, macd = computeMACD(closep)
        ema9 = ExpMovingAverage(macd, nema)

        ax2.plot(xLength[-SP:], macd[-SP:])
        ax2.plot(xLength[-SP:], ema9[-SP:])
        ax2.fill_between(xLength[-SP:], macd[-SP:]-ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
        ax2.yaxis.set_major_locator(mticker.MaxNLocator(nbins=4, prune='upper'))



        ax2.spines['bottom'].set_color("#5998ff")
        ax2.spines['top' ].set_color("#5998ff")
        ax2.spines['left'].set_color("#5998ff")
        ax2.spines['right'].set_color("#5998ff")
        ax2.tick_params(axis='x', colors='w')
        ax2.tick_params(axis='y', colors='w')

        ax2.text(0.015, 0.95, 'MACD 12, 26, 9', va='top', color='w', transform=ax2.transAxes)
        for label in ax2.xaxis.get_ticklabels():
            label.set_rotation(90)


# RSI plot
        ax0 = plt.subplot2grid((6,4), (0,0), sharex=ax1, rowspan=1, colspan=4, axisbg='#07000d')
        rsi = rsiFunc(closep)
        rsiCol = '#1a8782'
        poscol = '#386d13'
        negcol = '#8f2020'
        ax0.plot(xLength[-SP:], rsi[-SP:], '#8FF7F6', linewidth=1.5)
        ax0.fill_between(xLength[-SP:], rsi[-SP:], 70, where=(rsi[-SP:]>=70), alpha=0.5, facecolor='#ff1717', edgecolor=rsiCol)
        ax0.fill_between(xLength[-SP:], rsi[-SP:], 30, where=(rsi[-SP:]<=30), alpha=0.5, facecolor='#00FC43', edgecolor=rsiCol)
        ax0.axhline(70, color = negcol)
        ax0.axhline(30, color = poscol)
        ax0.spines['bottom'].set_color("#5998ff")
        ax0.spines['top' ].set_color("#5998ff")
        ax0.spines['left'].set_color("#5998ff")
        ax0.spines['right'].set_color("#5998ff")
        ax0.text(0.015, 0.95, 'RSI (14)', va='top', color='w', transform=ax0.transAxes)
        ax0.tick_params(axis='x', colors='w')
        ax0.tick_params(axis='y', colors='w')
        ax0.set_yticks([30,70])
        ax0.yaxis.label.set_color('w')












        plt.suptitle(stock, color='w')
        plt.setp(ax0.get_xticklabels(), visible=False)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.subplots_adjust(left=.10, bottom=.14, right=.93, top=.95, wspace=.20, hspace=0)

        #plt.show()
        #fig.savefig('savedChart.png', facecolor=fig.get_facecolor())


    except Exception as e:
        print('failed main loop',str(e))

fig = plt.figure(facecolor='#07000D')

def animate(i):
    graphData(stockToUse, 13, 50)


while True:
    stockToUse = input("Stock to chart (Leave blank to exit): ")
    if not stockToUse:
        print("Goodbye")
        break
    else:
        ani = animation.FuncAnimation(fig, animate, interval=1000)
        plt.show()