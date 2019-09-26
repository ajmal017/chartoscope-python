import time
import datetime
import numpy as np
from enum import Enum
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib.patches as patches
from mpl_finance import *

from chartoscope.core.library import StockFileReader
from chartoscope.core.extension import RenkoFileReader
from chartoscope.core.library import SmaIndicator, RsiIndicator, MacdIndicator

class CandlestickChart:
    def __init__(self, main_plot, grid_dimension, grid_location):
        self._grid_dimension = grid_dimension
        self._grid_location = grid_location
        self._dates = list(map(lambda item: item[0], main_plot.dataset))
        openp = list(map(lambda item: item[1], main_plot.dataset))
        highp = list(map(lambda item: item[2], main_plot.dataset))
        lowp = list(map(lambda item: item[3], main_plot.dataset))
        closep = list(map(lambda item: item[4], main_plot.dataset))
        volume = list(map(lambda item: item[5], main_plot.dataset))

        xLength = range(len(self._dates))  # length of the x-axis used for plotting coordinates (xLength, y)
        self._candles = list(zip(xLength, openp, highp, lowp, closep, volume))  # The data set
        # Formatter Class to eliminate weekend data gaps on chart

    def show(self):
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

        ax1= plt.subplot2grid(self._grid_dimension, self._grid_location, facecolor='#07000d')

        candlestick_ohlc(ax1, self._candles, width=0.75, colorup='#9eff15', colordown='#ff1717', alpha=0.75)

        ax1.xaxis.set_major_locator(mticker.MaxNLocator(30))
        ax1.xaxis.set_major_formatter(Jackarow('%Y%m%d', self._dates))
        ax1.spines['top'].set_color('#5998ff')
        ax1.spines['bottom'].set_color('#5998ff')
        ax1.spines['left'].set_color('#5998ff')
        ax1.spines['right'].set_color('#5998ff')
        ax1.spines['top'].set_color('#5998ff')
        ax1.tick_params(axis='y', colors='w')
        ax1.tick_params(axis='x', colors='w')

        plt.ylabel('Stock price', color='w')

        for label in ax1.xaxis.get_ticklabels():
            label.set_rotation(45)

        plt.xlabel('Date', color='w')


class RenkoChart:
    def __init__(self, dataset, grid_dimension, grid_location):
        self._dataset = dataset
        self._num_bars = 1000
        self._grid_dimension = grid_dimension
        self._grid_location = grid_location
        self._dates = list(map(lambda item: item[0], dataset.dataset))
        self._open = list(map(lambda item: item[1], dataset.dataset))
        self._close = list(map(lambda item: item[2], dataset.dataset))

        # create the figure
        #fig = plt.figure(1)
        #fig.clf()

    def show(self):
        self._axes = plt.subplot2grid(self._grid_dimension, self._grid_location, facecolor='#07000d')

        # plot the bars, blue for 'up', red for 'down'
        index = 1
        for item in self._dataset.dataset:
            open_price = item[1]
            close_price = item[2]
            if (open_price < close_price):
                renko = patches.Rectangle((index, open_price), 1, close_price - open_price, edgecolor='lightgreen',
                                          facecolor='blue', alpha=0.5)
                self._axes.add_patch(renko)
            else:
                renko = patches.Rectangle((index, open_price), 1, close_price - open_price, edgecolor='red',
                                          facecolor='red', alpha=0.5)
                self._axes.add_patch(renko)
            index = index + 1
        # adjust the axes
        plt.xlim([0, self._num_bars])
        plt.ylim([min(min(self._dates), min(self._close)), max(max(self._open), max(self._close))])
        # fig.suptitle(
        #    'Bars from ' + min(df['date_time']).strftime("%d-%b-%Y %H:%M") + " to " + max(df['date_time']).strftime(
        #        "%d-%b-%Y %H:%M") \
        #    + '\nPrice movement = ' + str(price_move), fontsize=14)

        self._axes.spines['top'].set_color('#5998ff')
        self._axes.spines['bottom'].set_color('#5998ff')
        self._axes.spines['left'].set_color('#5998ff')
        self._axes.spines['right'].set_color('#5998ff')
        self._axes.spines['top'].set_color('#5998ff')
        self._axes.tick_params(axis='y', colors='w')
        self._axes.tick_params(axis='x', colors='w')

        plt.xlabel('Bar Number', color='w')
        plt.ylabel('Price', color='w')
        plt.grid(True, linestyle='dotted')


class PlotType(Enum):
    Line = 1
    Ohlc = 2
    Stock = 3
    Renko = 4

class ChartArea:
    def __init__(self, main_plot, grid_dimension, grid_location):
        self._chart = None
        if main_plot.plot_info == PlotType.Stock:
            self._chart = CandlestickChart(main_plot, grid_dimension, grid_location)
        elif main_plot.plot_info == PlotType.Renko:
            self._chart = RenkoChart(main_plot, grid_dimension, grid_location)

    def show(self):
        self._chart.show()



class PlotInfo:
    def __init__(self, plot_type=None):
        self._plot_type = plot_type

    @property
    def plot_type(self):
        return self._plot_type

class ChartDataset:
    def __init__(self, dataset, plot_info=None):
        self._dataset = dataset
        self._plot_info = plot_info

    @property
    def dataset(self):
        return self._dataset

    @property
    def plot_info(self):
        return self._plot_info


class RenkoFileUtility:
    @staticmethod
    def load_dataset_from_file(renko_file):
        renko_reader = RenkoFileReader(renko_file)
        renko_reader.open()

        date_list = []
        dates = []
        openp = []
        closep = []

        target_bar_index = 1
        bar_size = 1000

        dateconverter = mdates.strpdate2num("%Y%m%d")
        counter = 0
        for row in renko_reader.read_all():
            counter += 1
            if counter >= target_bar_index:
                dates.append(dateconverter(row.timestamp.to_string("%Y%m%d")))
                date_list.append(row.timestamp.to_datetime())
                openp.append(row.open)
                closep.append(row.close)
            if counter == target_bar_index + bar_size:
                break

        renko_reader.close()

        x = 0
        y = len(dates)
        renkos = []
        while x < y:
            append_line = dates[x], openp[x], closep[x]
            renkos.append((append_line))
            x += 1

        return ChartDataset(renkos, PlotType.Renko)

class StockFileUtility:
    @staticmethod
    def load_dataset_from_file(stock_file):
        stock_reader = StockFileReader(stock_file)
        stock_reader.open()

        date_list = []
        dates = []
        openp = []
        highp = []
        lowp = []
        closep = []
        volume = []

        dateconverter = mdates.strpdate2num("%Y%m%d")
        for row in stock_reader.read_all():
            dates.append(dateconverter(row.timestamp.to_string("%Y%m%d")))
            date_list.append(row.timestamp.to_datetime())
            openp.append(row.open)
            highp.append(row.high)
            lowp.append(row.low)
            closep.append(row.adjusted_close)
            volume.append(row.volume)

        stock_reader.close()

        x = 0
        y = len(dates)
        candles = []
        while x < y:
            append_line = dates[x], openp[x], highp[x], lowp[x], closep[x], volume[x]
            candles.append((append_line))
            x += 1

        return ChartDataset(candles, PlotType.Stock)

class Multichart:
    def __init__(self, grid_dimension=(1, 1)):
        self._grid_dimension = grid_dimension
        self._chart_areas = []
        mpl.rcParams.update({'font.size': 8})

    def add_chart_area(self, main_plot, grid_location=None):
        chart_area = ChartArea(main_plot, self._grid_dimension, grid_location)
        self._chart_areas.append(chart_area)
        return chart_area

    def show(self):
        plt.figure(facecolor='#07000d')

        for chart_area in self._chart_areas:
            chart_area.show()

        plt.subplots_adjust(left=.10, bottom=.20, top=.90, wspace=.20, hspace=.40)
        plt.suptitle('Stock Price', color='w')
        plt.show()


multi_chart = Multichart((1, 1))

#ebay_stock_data = StockFileUtility.load_dataset_from_file('matplotlib_tutorial\\' + 'EBAY_2010_D1.stock')
#multi_chart.add_chart_area(ebay_stock_data, (0, 0))

#tsla_stock_data = StockFileUtility.load_dataset_from_file('matplotlib_tutorial\\' + 'TSLA_2011_D1.stock')
#multi_chart.add_chart_area(tsla_stock_data, (0, 1))

#aapl_stock_data = StockFileUtility.load_dataset_from_file('matplotlib_tutorial\\' + 'TSLA_2011_D1.stock')
#multi_chart.add_chart_area(aapl_stock_data, (1, 0))
eurusd_renko_data = RenkoFileUtility.load_dataset_from_file('EURUSD_2017_07_R10.renko')
chart_area = multi_chart.add_chart_area(eurusd_renko_data, (0, 0))
#rsi_indicator = RsiIndicator(14, 1000)
#rsi_indicator.calculate_all(eurusd_renko_data.dataset, timestamp_index=0, value_index=1)
#chart_area.add_subplot()

multi_chart.show()
