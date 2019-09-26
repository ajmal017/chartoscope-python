import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from enum import Enum
from chartoscope.core.extension import RenkoFileReader
from chartoscope.core.library import HmaIndicator, RsiIndicator
from chartoscope.core.common import MarketPosition
import sys

class PlotType(Enum):
    Line = 1
    Ohlc = 2
    Stock = 3
    Renko = 4

class ChartDataset:
    def __init__(self, dataset, plot_info=None):
        self._dataset = dataset

    @property
    def dataset(self):
        return self._dataset

class RenkoFileUtility:
    @staticmethod
    def load_dataset_from_file(renko_file):
        renko_reader = RenkoFileReader(renko_file)
        renko_reader.open()

        hma_100 = HmaIndicator(180, 1001)
        rsi_14 = RsiIndicator(20, 1001)


        date_list = []
        dates = []
        openp = []
        closep = []
        hma_value = []
        hma_roc = []
        hma_reversed = []
        rsi_value = []

        target_bar_index = 23000
        bar_size = 1000

        dateconverter = mdates.strpdate2num("%Y%m%d %H:%M:%S")
        counter = 0
        for row in renko_reader.read_all():
            counter += 1
            hma_100.calculate(row.timestamp, row.close)
            rsi_14.calculate(row.timestamp, row.close)
            if counter >= target_bar_index:
                dates.append(dateconverter(row.timestamp.to_string("%Y%m%d %H:%M:%S")))
                date_list.append(row.timestamp.to_datetime())
                openp.append(row.open)
                closep.append(row.close)

                hma_value.append(hma_100.current.value)
                hma_roc.append(hma_100.rate_of_change)
                hma_reversed.append(hma_100.has_reversed)
                rsi_value.append(rsi_14.current.relative_strength_index)
            if counter == target_bar_index + bar_size:
                break

        renko_reader.close()

        x = 0
        y = hma_100.length-1
        renkos = []
        while x <= y:
            append_line = dates[x], openp[x], closep[x], hma_value[x], hma_roc[x], hma_reversed[x]
            renkos.append((append_line))
            x += 1

        return ChartDataset(renkos, PlotType.Renko)


def PlotRenko(dataset):
    class Jackarow(mdates.DateFormatter):
        def __init__(self, fmt, dates):
            mdates.DateFormatter.__init__(self, fmt)
            self._dates = dates

        def __call__(self, x, pos=0):
            # This gets called even when out of bounds, so IndexError must be prevented.
            if x < 0:
                x = 0
            elif x >= len(self._dates):
                x = -1
            return mdates.DateFormatter.__call__(self, self._dates[int(x)], pos)

    def buy_signal(axes, x_value, y_values):
        axes.annotate('buy', xy=(x_value, y_values[x_value] - 0.0005), xytext=(x_value, y_values[x_value] - 0.001),
                      arrowprops=dict(facecolor='green', shrink=0.05),)


    def sell_signal(axes, x_value, y_values):
        axes.annotate('sell', xy=(x_value, y_values[x_value] + 0.001), xytext=(x_value, y_values[x_value] + 0.0014),
                      arrowprops=dict(facecolor='red', shrink=0.05),)

    def rsi_signal(axes, rsi_value, x_value, y_values):
        axes.annotate('rsi@{0}'.format(rsi_value), xy=(x_value, y_values[x_value] + 0.0015), xytext=(x_value, y_values[x_value] + 0.002),
                      arrowprops=dict(facecolor='yellow', shrink=0.05),)

    # number of bars to display in the plot
    num_bars = len(dataset.dataset)

    dates = list(map(lambda item: item[0], dataset.dataset))
    open = list(map(lambda item: item[1], dataset.dataset))
    close = list(map(lambda item: item[2], dataset.dataset))
    hma_indicator1 = list(map(lambda item: item[3], dataset.dataset))
    hma_reversed = list(map(lambda item: item[5], dataset.dataset))

    # create the figure
    fig = plt.figure(1)
    fig.clf()
    axes = fig.gca()

    # plot the bars, blue for 'up', red for 'down'
    index = 1
    for item in dataset.dataset:
        open_price = item[1]
        close_price = item[2]
        hma_value = item[3]
        hma_roc = item[4]
        if (open_price < close_price):
            renko = patches.Rectangle((index, open_price), 1, close_price - open_price, edgecolor='darkblue',
                                                 facecolor='blue', alpha=0.5)
            axes.add_patch(renko)
        else:
            renko = patches.Rectangle((index, open_price), 1, close_price - open_price, edgecolor='darkred',
                                                 facecolor='red', alpha=0.5)
            axes.add_patch(renko)

        index = index + 1

    index_values = range(num_bars)
    # adjust the axes
    plt.xlim([0, num_bars])
    plt.ylim([min(min(dates), min(close)), max(max(open), max(close))])
    axes.plot(index_values, hma_indicator1)
    axes.xaxis.set_major_locator(mticker.MaxNLocator(30))
    axes.xaxis.set_major_formatter(Jackarow('%Y%m%d %H:%M:%S', dates))
    #fig.suptitle(
    #    'Bars from ' + min(df['date_time']).strftime("%d-%b-%Y %H:%M") + " to " + max(df['date_time']).strftime(
    #        "%d-%b-%Y %H:%M") \
    #    + '\nPrice movement = ' + str(price_move), fontsize=14)


    index = 0
    is_buy = False
    is_sell = False
    buy_price = 0
    sell_price = 0
    profit_target = 0
    entry_price = None
    entry_position = MarketPosition.NoPosition
    target_reversal = None
    total_pnl = 0
    for item in dataset.dataset:
        hma_roc = item[4]

        if entry_position == MarketPosition.NoPosition:
            if hma_roc > 90 and (target_reversal is None or (target_reversal is not None and target_reversal == MarketPosition.Long)):
                print(hma_roc)
                entry_price = close[index]
                buy_signal(axes, index, close)
                entry_position = MarketPosition.Long
                target_reversal == None
            elif hma_roc < - 90 and (target_reversal is None or (target_reversal is not None and target_reversal == MarketPosition.Short)):
                print(hma_roc)
                entry_price = close[index]
                sell_signal(axes, index, close)
                entry_position = MarketPosition.Short
                target_reversal == None
        else:
            if entry_position == MarketPosition.Short and (hma_reversed[index]):
                pnl = (entry_price - close[index]) * 10000
                print('Closing sell @P/L {0}'.format(pnl))
                total_pnl += pnl
                entry_position = MarketPosition.NoPosition
                target_reversal = MarketPosition.Long
            elif entry_position == MarketPosition.Long and (hma_reversed[index]):
                pnl = (close[index] - entry_price) * 10000
                print('Closing buy @P/L {0}'.format(pnl))
                total_pnl += pnl
                entry_position = MarketPosition.NoPosition
                target_reversal = MarketPosition.Short

        #if rsi_indicator[index] > 70:
        #    rsi_signal(axes, rsi_indicator[index], index, close)

        index += 1

    print("Total P/L: {0}".format(total_pnl))
    fig.autofmt_xdate()
    plt.xlabel('Bar Number')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()


dataset = RenkoFileUtility.load_dataset_from_file('EURUSD_2013_04_R1.renko')
PlotRenko(dataset)