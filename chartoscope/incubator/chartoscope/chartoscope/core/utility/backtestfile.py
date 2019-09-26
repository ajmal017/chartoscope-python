from chartoscope.core.common import CustomFileAppender, CustomFileReader, CustomColumnType, CustomBinaryFileInfo, MarketPosition
import pandas as pd
import numpy as np

class BacktestFileInfo(CustomBinaryFileInfo):
    FileMarker = 'backtest'

    def __init__(self):
        super().__init__(BacktestFileInfo.FileMarker)

        self.add_timestamp_column(self._columns)

        self._columns.append("entry_price", CustomColumnType.Float)
        self._columns.append("position", CustomColumnType.Integer)
        self._columns.append("exit_price", CustomColumnType.Float)

        self.refresh_header()


class BacktestFileAppender(CustomFileAppender):
    def __init__(self, file_name):
        super().__init__(file_name, BacktestFileInfo())

    def append(self, timestamp_value, entry_price, position, exit_price):
        date_time_split = timestamp_value.tick_split
        self._append(date_time_split[0], date_time_split[1], date_time_split[2], entry_price, position,
                     exit_price)


class BacktestFileReader(CustomFileReader):
    def __init__(self, file_name):
        super().__init__(file_name, BacktestFileInfo())

    def read(self):
        data = self._read()
        if data is None:
            return None
        else:
            values = {"timestamp": CustomBinaryFileInfo.read_timestamp(data, 0, 1, 2)}
            values["entry_price"] = data[3]
            values["position"] = MarketPosition(data[4])
            values["exit_price"] = data[5]

            return values


class BacktestSignalFileStats:
    def __init__(self, signal_file):
        self._signal_file = signal_file

    def generate(self):
        signal_reader = BacktestFileReader(self._signal_file)

        with signal_reader.open():
            signals = list(signal_reader.read_all())

        df = pd.DataFrame(signals)

        df["day"] = pd.Series(map(lambda item: item.to_string("%Y%m%d"), df["timestamp"]), index=df.index)
        df["position"] = pd.Series(map(lambda item: str(item), df["position"]), index=df.index)

        df["timestamp"] = pd.Series(map(lambda item: item.to_string("%Y%m%d %H:%M:%S"), df["timestamp"]),
                                    index=df.index)

        df["profit_loss"] = pd.Series(map(lambda index: df["entry_price"][index] - df["exit_price"][index]
        if df["position"][index] == MarketPosition.Short else df["exit_price"][index] - df["entry_price"][index],
                                          df.index), index=df.index)

        df["rolling_profit_loss"] = pd.Series([sum(df["profit_loss"][:index+1]) for index in range(0, len(df))], index=df.index)

        df["start_of_day"] = pd.Series([True if index==0 else df["day"][index-1]!=df["day"][index] for index in range(0, len(df))], index=df.index)

        df["prev_rolling_profit_loss"] = pd.Series(
            [0 if index == 0 else df["rolling_profit_loss"][index - 1] for index in range(0, len(df))],
            index=df.index)

        df2 = df[df["start_of_day"]==True][["prev_rolling_profit_loss","day"]]

        df3 = pd.merge(df, df2, on='day', how='left', suffixes=('','_start_of_day'))

        df3["daily_rolling_profit_loss"] = pd.Series(
            [df3["prev_rolling_profit_loss"][index]-df3["prev_rolling_profit_loss_start_of_day"][index]+df3["profit_loss"][index] for index in range(0, len(df))],
            index=df.index)

        df4 = df3.groupby("day").agg({"daily_rolling_profit_loss": np.max})

        df4["max_daily_rolling_profit_loss"] = pd.Series(map(lambda item: round(item * 10000,2), df4["daily_rolling_profit_loss"]),
                                    index=df4.index)

        # df["start_of_day_profit_loss"] = pd.Series(
        #      [df[np.logical_and(df["day"]==df["day"][index],df["start_of_day"])]["prev_rolling_profit_loss"][0] for index in range(0, len(df))],
        #      index=df.index)

        writer = pd.ExcelWriter('output.xlsx')

        df3.to_excel(writer, 'Sheet1')
        df4.to_excel(writer, 'Sheet2')
        writer.save()

        long_pnl = df[df["position"] == MarketPosition.Long]["profit_loss"].sum() * 10000
        print("Long P/L: {0}".format(long_pnl))

        short_pnl = df[df["position"] == MarketPosition.Short]["profit_loss"].sum() * 10000
        print("Short P/L: {0}".format(short_pnl))

        total_pnl = df["profit_loss"].sum() * 10000
        print("Total P/L: {0}".format(total_pnl))

        max_drawdown = df["profit_loss"].min() * 10000
        print("Maximum Drawdown: {0}".format(max_drawdown))

        max_winning = df["profit_loss"].max() * 10000
        print("Maximum Winning: {0}".format(max_winning))

        ave_daily_pnl = df.groupby("day").agg({'profit_loss': np.mean})["profit_loss"].mean() * 10000
        print("Average Daily P/L: {}".format(ave_daily_pnl))

        ave_daily_drawdown = df[df["profit_loss"] < 0].groupby("day").agg({'profit_loss': np.mean})[
                                 "profit_loss"].mean() * 10000
        print("Average Daily Drawdown: {}".format(ave_daily_drawdown))

        ave_daily_positions = int(df.groupby("day").size().mean())
        print("Average Daily Positions: {}".format(ave_daily_positions))

        total_positions = len(df)
        print("Total Positions: {}".format(total_positions))

        total_winning_positions = df[df["profit_loss"] > 0]["day"].count()
        print("Total Winning Positions: {}".format(total_winning_positions))

        total_losing_positions = df[df["profit_loss"] < 0]["day"].count()
        print("Total Losing Positions: {}".format(total_losing_positions))

        win_ratio = int((total_winning_positions / (total_winning_positions + total_losing_positions)) * 10)
        lose_ratio = int((total_losing_positions / (total_winning_positions + total_losing_positions)) * 10)

        print("Win/Loss Ratio: {}:{}".format(win_ratio, lose_ratio))