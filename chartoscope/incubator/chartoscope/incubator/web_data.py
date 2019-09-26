from pandas_datareader import data, wb
from chartoscope.core.common import Timestamp
from chartoscope.core.library.stock import StockFileAppender
import datetime
from dateutil import parser

# We will look at stock prices over the past year, starting at January 1, 2016
start = datetime.datetime(2010, 8, 26)
end = datetime.datetime(2013, 8, 27)

# Let's get Apple stock data; Apple's ticker symbol is AAPL
# First argument is the series we want, second is the source ("yahoo" for Yahoo! Finance), third is the start date, fourth is the end date
apple = data.DataReader("EBAY", "yahoo", start, end)

print(apple.columns.values)

appender = StockFileAppender("EBAY_2010_D1.stock")
appender.open()

for row in apple.itertuples(index=True, name='Pandas'):
    timestamp= getattr(row, "Index")
    appender.append(Timestamp(datetime_value= timestamp),
                    float(getattr(row, "Open")), float(getattr(row, "High")),
                    float(getattr(row, "Low")), float(getattr(row, "Close")),
                    float(getattr(row, "_5")), int(getattr(row, "Volume"))
                    )

appender.close()