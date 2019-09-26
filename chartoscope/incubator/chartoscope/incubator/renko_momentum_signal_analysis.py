from chartoscope.core.utility import BacktestFileReader
from chartoscope.core.common import MarketPosition
import pandas as pd
import numpy as np

class BacktestSignalFileStats:
    def __init__(self, signal_file):
        self._signal_file = signal_file

    def generate(self):
        signal_reader = BacktestFileReader(self._signal_file)

        with signal_reader.open():
            signals = list(signal_reader.read_all())


        df = pd.DataFrame(signals)

        df["day"] = pd.Series(map(lambda item: item.to_string("%Y%m%d"), df["timestamp"]), index=df.index)

        df["timestamp"] = pd.Series(map(lambda item: item.to_string("%Y%m%d %H:%M:%S"), df["timestamp"]), index=df.index)

        df["profit_loss"] = pd.Series(map(lambda index: df["entry_price"][index]-df["exit_price"][index]
            if df["position"][index]==MarketPosition.Short else df["exit_price"][index]-df["entry_price"][index], df.index), index=df.index)

        long_pnl = df[df["position"] == MarketPosition.Long]["profit_loss"].sum() * 10000
        print("Long P/L: {0}".format(long_pnl))

        short_pnl = df[df["position"] == MarketPosition.Short]["profit_loss"].sum() * 10000
        print("Short P/L: {0}".format(short_pnl))

        total_pnl = df["profit_loss"].sum() * 10000
        print("Total P/L: {0}".format(total_pnl))

        max_drawdown = df["profit_loss"].min() * 10000
        print("Maximum Drawdown: {0}".format(max_drawdown))

        ave_daily_pnl = df.groupby("day").agg({'profit_loss': np.mean})["profit_loss"].mean() * 10000
        print("Average Daily P/L: {}".format(ave_daily_pnl))

        ave_daily_drawdown = df[df["profit_loss"] < 0].groupby("day").agg({'profit_loss': np.mean})["profit_loss"].mean() * 10000
        print("Average Daily Drawdown: {}".format(ave_daily_drawdown))

        ave_daily_positions = int(df.groupby("day").size().mean())
        print("Average Daily Positions: {}".format(ave_daily_positions))

        total_positions = len(df)
        print("Total Positions: {}".format(total_positions))

        total_winning_positions = df[df["profit_loss"] > 0]["day"].count()
        print("Total Winning Positions: {}".format(total_winning_positions))

        total_losing_positions = df[df["profit_loss"] < 0]["day"].count()
        print("Total Losing Positions: {}".format(total_losing_positions))

        win_ratio = int((total_winning_positions/(total_winning_positions + total_losing_positions)) * 10)
        lose_ratio = int((total_losing_positions/(total_winning_positions + total_losing_positions)) * 10)

        print("Win/Loss Ratio: {}:{}".format(win_ratio, lose_ratio))
