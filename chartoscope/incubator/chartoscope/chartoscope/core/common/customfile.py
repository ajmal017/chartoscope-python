from enum import Enum
import struct
from chartoscope.core.common import BinaryFileAppender, BinaryFileReader, BinaryFileInfo, Timestamp, TimestampConverter

class CustomColumnType(Enum):
    Integer = 'i'
    Float = 'f'
    Bool = '?'

class CustomColumn:
    def __init__(self, name, item_type):
        self._name = name
        self._item_type = item_type

    @property
    def name(self):
        return self._name

    @property
    def item_type(self):
        return self._item_type

class CustomColumns:
    def __init__(self):
        self.column_info = []

    def append(self, custom_item_name=None, custom_item_type=None, custom_item=None):
        if (custom_item is None):
            self.column_info.append(CustomColumn(custom_item_name, custom_item_type))
        else:
            self.column_info.append(custom_item)

    @property
    def items(self):
        return self.column_info


class CustomBinaryFileInfo(BinaryFileInfo):
    def __init__(self, file_marker):
        super().__init__(file_marker)
        self.file_marker = file_marker
        self._columns = CustomColumns()

    def refresh_header(self):
        self.header_format.update_format(''.join(list(map(lambda item: item.item_type.value,
                                                                self._columns.column_info))))

    @staticmethod
    def add_timestamp_column(columns_list, include_time=True, include_microsecond=True):
        columns_list.append(custom_item=CustomColumn("date_tick", CustomColumnType.Integer))
        if include_time:
            columns_list.append(custom_item=CustomColumn("time_tick", CustomColumnType.Integer))
            if include_microsecond:
                columns_list.append(custom_item=CustomColumn("microsecond_tick", CustomColumnType.Integer))

    @staticmethod
    def read_timestamp(data_list, date_index=0, time_index=1, microsecond_index=2):
        if date_index is None:
            return None
        else:
            if time_index is None:
                return TimestampConverter.from_tick_split(data_list[date_index])
            elif microsecond_index is None:
                return TimestampConverter.from_tick_split(data_list[date_index], data_list[time_index])
            else:
                return TimestampConverter.from_tick_split(data_list[date_index], data_list[time_index],
                                                          data_list[microsecond_index])

class CustomFileAppender(BinaryFileAppender):
    def __init__(self, file_name, custom_binary_file_info):
        super().__init__(file_name, custom_binary_file_info)

    def _append(self, *args):
        row_data = struct.pack(self._file_info.header_format.format, *args)
        super()._append(row_data)

class CustomFileReader(BinaryFileReader):
    def __init__(self, file_name, custom_binary_file_info):
        super().__init__(file_name, custom_binary_file_info)

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            return data

    def read_all(self):
        if not self._file_context._is_file_open:
            raise Exception("File is not open.")
        result = self.read()
        while result is not None:
            yield result
            result = self.read()