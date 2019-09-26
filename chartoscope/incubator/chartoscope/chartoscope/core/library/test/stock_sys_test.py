from chartoscope.core.library.stock import StockFileAppender, StockFileReader
from chartoscope.core.common import Timestamp
import tempfile
import os

def test_stock_file_append():
    tempFile = tempfile.mktemp()
    appender = StockFileAppender(tempFile)
    appender.open()

    orig_size = os.stat(tempFile).st_size

    for x in range(31):
        timestamp = Timestamp(2017, 1, x + 1)
        appender.append(timestamp, 1, 2, 3, 4, 5, 6)

    appender.close()

    assert(os.stat(tempFile).st_size > orig_size)

def test_stock_file_readall():
    tempFile = tempfile.mktemp()
    appender = StockFileAppender(tempFile)
    appender.open()

    for x in range(31):
        timestamp = Timestamp(2017, 1, x + 1)
        appender.append(timestamp, 1, 2, 3, 4, 5, 6)

    appender.close()

    reader= StockFileReader(tempFile)
    reader.open()

    row_counter= 0
    for row in reader.read_all():
        row_counter += 1

    assert(row_counter == 31)

