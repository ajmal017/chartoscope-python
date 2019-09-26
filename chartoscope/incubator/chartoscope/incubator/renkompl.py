import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from enum import Enum
from chartoscope.core.extension import RenkoFileReader
from chartoscope.core.library import HmaIndicator
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

        hma_100 = HmaIndicator(200, 1001)


        date_list = []
        dates = []
        openp = []
        closep = []
        hma_value = []
        hma_roc = []

        target_bar_index = 11000
        bar_size = 1000

        dateconverter = mdates.strpdate2num("%Y%m%d %H:%M:%S")
        counter = 0
        for row in renko_reader.read_all():
            counter += 1
            result = hma_100.calculate(row.timestamp, row.close)

            if counter >= target_bar_index:
                dates.append(dateconverter(row.timestamp.to_string("%Y%m%d %H:%M:%S")))
                date_list.append(row.timestamp.to_datetime())
                openp.append(row.open)
                closep.append(row.close)

                hma_value.append(hma_100.current.value)
                hma_roc.append(hma_100.rate_of_change)
            if counter == target_bar_index + bar_size:
                break

        renko_reader.close()

        x = 0
        y = hma_100.length-1
        renkos = []
        while x <= y:
            append_line = dates[x], openp[x], closep[x], hma_value[x], hma_roc[x]
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

    def buy_signal(axes, pnl, x_value, y_values):
        axes.annotate('buy\n@P/L {0}'.format(pnl), xy=(x_value, y_values[x_value] - 0.0005), xytext=(x_value, y_values[x_value] - 0.001),
                      arrowprops=dict(facecolor='green', shrink=0.05),)


    def sell_signal(axes, pnl, x_value, y_values):
        axes.annotate('sell\n@P/L {0}'.format(pnl), xy=(x_value, y_values[x_value] + 0.001), xytext=(x_value, y_values[x_value] + 0.0014),
                      arrowprops=dict(facecolor='red', shrink=0.05),)

    # number of bars to display in the plot
    num_bars = len(dataset.dataset)

    dates = list(map(lambda item: item[0], dataset.dataset))
    open = list(map(lambda item: item[1], dataset.dataset))
    close = list(map(lambda item: item[2], dataset.dataset))
    hma_indicator1 = list(map(lambda item: item[3], dataset.dataset))

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
    for item in dataset.dataset:
        hma_roc = item[4]
        if hma_roc > 10:
            if not is_buy:
                if close[index] < profit_target:
                    pnl = (sell_price - close[index]) * 10000
                    buy_signal(axes,pnl, index, close)
                    profit_target = close[index] + (1/(5 * 10000))
                    buy_price = close[index]
                is_buy = True
                is_sell = False
        elif hma_roc < 10:
            if not is_sell:
                if close[index] > profit_target:
                    pnl = (close[index] - buy_price) * 10000
                    sell_signal(axes, pnl, index, close)
                    profit_target = close[index] - (1/(5 * 10000))
                    sell_price = close[index]
                is_sell = True
                is_buy = False

        index += 1

    fig.autofmt_xdate()
    plt.xlabel('Bar Number')
    plt.ylabel('Price')
    plt.grid(True)
    plt.show()


dataset = RenkoFileUtility.load_dataset_from_file('EURUSD_2013_04_R1.renko')
PlotRenko(dataset)