from enum import Enum


class TimeUnit(Enum):
    Minute = 1
    Hour = 2
    Day = 3
    Month = 4


class Timeframe:
    def __init__(self, time_unit, units):
        self.time_unit = time_unit
        self.units = units


class TimeframeInterval:
    M1 = Timeframe(TimeUnit.Minute, 1)
    M5 = Timeframe(TimeUnit.Minute, 5)
    M10 = Timeframe(TimeUnit.Minute, 10)
    M30 = Timeframe(TimeUnit.Minute, 30)
    H1 = Timeframe(TimeUnit.Hour, 1)
    H4 = Timeframe(TimeUnit.Hour, 4)
    D1 = Timeframe(TimeUnit.Day, 1)
