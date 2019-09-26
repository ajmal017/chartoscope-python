import matplotlib
from ohlc_aggregator import *
from tzlocal import get_localzone

matplotlib.use('Qt5Agg')
from PyQt5 import QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT
from matplotlib.figure import Figure

from mpl_finance import *
import matplotlib.dates as mdates


def bytespdate2num(fmt, encoding='utf-8'):
    strconverter = mdates.strpdate2num(fmt)

    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)

    return bytesconverter

def getTimestamp(datetimeFeed):
    return Timestamp(year= datetimeFeed[0][0], month= datetimeFeed[0][1], day= datetimeFeed[0][2], hour= datetimeFeed[0][3], minute=datetimeFeed[0][4], second=datetimeFeed[0][5])

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self._fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self._fig.add_subplot(111)

        FigureCanvas.__init__(self, self._fig)
        self.compute_initial_figure()

        self.setParent(parent)

        FigureCanvas.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MultichartCanvas(MplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self, *args, **kwargs):
        MplCanvas.__init__(self, *args, **kwargs)

    def compute_initial_figure(self):
        toolbar = NavigationToolbar2QT(self, self)
        toolbar.update()
        self.axes.yaxis.tick_right()

    def plotOHLC(self):
        dataFeed = [
            ((2017, 1, 1, 0, 0, 0), 5.1, 5.1),
            ((2017, 1, 1, 0, 0, 20), 2.1, 2.1),
            ((2017, 1, 1, 0, 0, 40), 6.1, 6.1),
            ((2017, 1, 1, 0, 0, 50), 2.1, 2.1),
            ((2017, 1, 1, 0, 1, 0), 3.1, 3.1),
            ((2017, 1, 1, 0, 1, 34), 4.1, 4.1),
            ((2017, 1, 1, 0, 1, 44), 3.1, 3.1),
            ((2017, 1, 1, 0, 1, 54), 1.1, 1.1),
            ((2017, 1, 1, 0, 2, 1), 2.1, 2.1),
            ((2017, 1, 1, 0, 3, 0), 3.1, 3.1),
            ((2017, 1, 1, 0, 4, 34), 4.1, 4.1),
            ((2017, 1, 1, 0, 5, 44), 3.1, 3.1),
            ((2017, 1, 1, 0, 6, 54), 1.1, 1.1),
            ((2017, 1, 1, 0, 7, 1), 2.1, 2.1)
        ]
        ohlcAggregator = OhlcAggregator(TimeframeInterval.M1)
        priceIndex = 0
        ohlcAggregator.initialize(getTimestamp(dataFeed[priceIndex]), dataFeed[priceIndex][1], dataFeed[priceIndex][2])
        priceIndex += 1
        ohlcBars = OhlcBars(10)

        while priceIndex < len(dataFeed):
            ohlcAggregator.price_action(getTimestamp(dataFeed[priceIndex]), dataFeed[priceIndex][1],
                                        dataFeed[priceIndex][2], ohlcBars)
            priceIndex += 1

        # ohlcbars = [(b'20170531', 1.685955, 1.685975, 1.68586, 1.68586, 151),
        #             (b'20170530', 1.6859, 1.68605, 1.6859, 1.685955, 171),
        #             (b'20170529', 1.685855, 1.68591, 1.685805, 1.6859, 152),
        #             (b'20170528', 1.68588, 1.68589, 1.685815, 1.685855, 173),
        #             (b'20170527', 1.685955, 1.685955, 1.68585, 1.68588, 153),
        #             (b'20170526', 1.68593, 1.68597, 1.685925, 1.685955, 120),
        #             (b'20170525', 1.686, 1.686045, 1.68593, 1.68593, 132),
        #             (b'20170524', 1.68602, 1.686045, 1.686, 1.686, 100),
        #             (b'20170523', 1.686175, 1.686175, 1.68602, 1.68602, 148),
        #             (b'20170522', 1.68602, 1.68618, 1.68601, 1.686175, 133)]

        x = 0
        y = ohlcBars.length

        ohlc = []

        strconverter = mdates.strpdate2num('%Y%m%d %H:%M')

        tz = get_localzone()

        while x < y:
            dt= ohlcBars[x].timestamp.to_datetime()
            strdt= dt.astimezone(tz).strftime('%Y%m%d %H:%M')
            append_me = strconverter(strdt), ohlcBars[x].open, ohlcBars[x].high, ohlcBars[x].low, ohlcBars[x].close, 1
            ohlc.append(append_me)
            x += 1

        print(ohlc)
        candlestick_ohlc(self.axes, ohlc, width=0.0001, colorup='#77d879', colordown='#db3f3f')

        for label in self.axes.xaxis.get_ticklabels():
            label.set_rotation(45)

        self.axes.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d %H:%M'))
        #self.axes.xaxis.set_major_locator(mticker.MaxNLocator(6))
        self.axes.grid(True)

        self.axes.set_xlabel('Date')
        self.axes.set_ylabel('Price')
        self.axes.set_title('Sine Wave')
        self.axes.legend()