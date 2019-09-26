class TimeSeriesFileInfo(BinaryFileInfo):
    def __init__(self):
        super().__init__("ts")

    def add_timestamp_column(self, include_time=True, include_microsecond=True):
        columns_list.append(custom_item=CustomColumn("date_tick", CustomColumnType.Integer))
        if include_time:
            columns_list.append(custom_item=CustomColumn("time_tick", CustomColumnType.Integer))
            if include_microsecond:
                columns_list.append(custom_item=CustomColumn("microsecond_tick", CustomColumnType.Integer))

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