import pandas as pd


class DataFrame:
    def __init__(self):
        pass

    def series(self, item_value_lambda, timestamp_format='%Y%m%d %H:%M:%S'):
        index = 0
        index_names = []
        values = []
        while index < self.length:
            index_names.append(self[index].timestamp.to_string(timestamp_format))
            values.append(item_value_lambda(self[index]))
            index += 1

        return pd.Series(values, index_names)
