from chartoscope.core.library import *
from chartoscope.core.common import *
from collections import namedtuple

BidAskFileRecord = namedtuple('BidAskFileRecord', 'timestamp bid ask')


class BidAskFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__('bidask', BinaryFileHeaderFormat('iiiff'))


class BidAskFileAppender(BinaryFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, BidAskFileInfo())

    def append(self, timestamp_value, bid, ask):
        date_time_split = timestamp_value.tick_split
        row_data = struct.pack(self._file_info.headerFormat.format, date_time_split[0], date_time_split[1],
                               date_time_split[2], bid, ask)
        self._append(row_data)


class BidAskFileReader(BinaryFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, BidAskFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return BidAskFileRecord(TimestampConverter.from_tick_split(data[0], data[1], data[2]), data[3], data[4])

    def read_all(self):
        if not self._file_context._is_file_open:
            raise Exception("File is not open.")
        result = self.read()
        while result is not None:
            yield result
            result = self.read()

class BidAskCatalogFileAppender:
    def __init__(self, catalog_file_name):
        self._catalog_file_name = catalog_file_name



class BidAskCatalogFileNavigator:
    def __init__(self, catalog):
        self._catalog = catalog
        self._readers = None

    def seek(self, timestamp_value):
        pass

    def skip(self, record_offset=1):
        pass

    @property
    def eof(self):
        pass



