from chartoscope.core.common import CustomFileAppender, CustomFileReader, CustomColumns, CustomColumnType, CustomBinaryFileInfo, TimestampConverter

class RenkoProbeFileInfo(CustomBinaryFileInfo):
    FileMarker = 'renkoprb'

    def __init__(self):
        super().__init__(RenkoProbeFileInfo.FileMarker)

        self.add_timestamp_column(self._columns)

        self._columns.append("open", CustomColumnType.Float)
        self._columns.append("close", CustomColumnType.Float)
        self._columns.append("hma", CustomColumnType.Float)
        self._columns.append("hma_reversed", CustomColumnType.Bool)
        self._columns.append("roc", CustomColumnType.Float)

        self.refresh_header()


class RenkoProbeWriter(CustomFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, RenkoProbeFileInfo())

    def append(self, timestamp_value, open_price, close_price, hma_value, hma_reversed, roc_value):
        date_time_split = timestamp_value.tick_split
        self._append(date_time_split[0], date_time_split[1], date_time_split[2], open_price, close_price,
                     hma_value, hma_reversed, roc_value)


class RenkoProbeReader(CustomFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, RenkoProbeFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            values = {"timestamp": CustomBinaryFileInfo.read_timestamp(data, 0, 1, 2)}
            for index in range(3, len(self._file_info._columns.column_info)):
                values[self._file_info._columns.column_info[index].name] = data[index]

            return values

