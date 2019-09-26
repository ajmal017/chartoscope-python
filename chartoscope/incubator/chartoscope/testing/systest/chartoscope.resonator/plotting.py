import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from mpl_finance import *

def bytespdate2num(fmt, encoding='utf-8'):
    strconverter = mdates.strpdate2num(fmt)

    def bytesconverter(b):
        s = b.decode(encoding)
        return strconverter(s)

    return bytesconverter


def graph_data(stock):
    fig = plt.figure()
    ax1 = plt.subplot2grid((1, 1), (0, 0))
    dateconverter= bytespdate2num('%Y%m%d')
    dateval= dateconverter(b'20170721')
    date=[dateconverter(b'20170721'), dateconverter(b'20170722'), dateconverter(b'20170723'), dateconverter(b'20170724')]
    openp=[149.9900,149.9900,149.9900,149.9900]
    highp = [149.9900,149.9900,149.9900,149.9900]
    lowp = [149.9900,149.9900,149.9900,149.9900]
    closep = [149.9900,149.9900,149.9900,149.9900]
    volume = [149.9900,149.9900,149.9900,149.9900]

    ohlcbars= [(b'20170531', 1.685955, 1.685975, 1.68586, 1.68586, 151),
     (b'20170530', 1.6859, 1.68605, 1.6859, 1.685955, 171),
     (b'20170529', 1.685855, 1.68591, 1.685805, 1.6859, 152),
     (b'20170528', 1.68588, 1.68589, 1.685815, 1.685855, 173),
     (b'20170527', 1.685955, 1.685955, 1.68585, 1.68588, 153),
     (b'20170526', 1.68593, 1.68597, 1.685925, 1.685955, 120),
     (b'20170525', 1.686, 1.686045, 1.68593, 1.68593, 132),
     (b'20170524', 1.68602, 1.686045, 1.686, 1.686, 100),
     (b'20170523', 1.686175, 1.686175, 1.68602, 1.68602, 148),
     (b'20170522', 1.68602, 1.68618, 1.68601, 1.686175, 133)]
    x = 0
    y = len(ohlcbars)
    ohlc = []

    while x < y:
        append_me = dateconverter(ohlcbars[x][0]),ohlcbars[x][1],ohlcbars[x][2],ohlcbars[x][3],ohlcbars[x][4]
        ohlc.append(append_me)
        x += 1

    candlestick_ohlc(ax1, ohlc, width=0.4, colorup='#77d879', colordown='#db3f3f')

    ax1.yaxis.tick_right()

    for label in ax1.xaxis.get_ticklabels():
        label.set_rotation(45)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.grid(True)


    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title(stock)
    plt.legend()
    plt.subplots_adjust(left=0.09, bottom=0.20, right=0.94, top=0.90, wspace=0.2, hspace=0)
    plt.show()


graph_data('EBAY')