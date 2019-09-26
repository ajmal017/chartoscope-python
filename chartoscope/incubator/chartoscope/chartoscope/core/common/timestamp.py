import datetime
import math
import pytz
from dateutil import relativedelta


class Timestamp:
    def __init__(self, year=None, month=None, day=None, hour=0, minute=0, second=0, microsecond=0, datetime_value=None,
                 tz_info=None):
        if datetime_value is None:
            if year is not None and month is not None and day is not None:
                self._year = year
                self._month = month
                self._day = day
                self._hour = hour
                self._minute = minute
                self._second = second
                self._microsecond = microsecond
            else:
                raise Exception("Must specify year, month and day values.")
        else:
            self._year = datetime_value.year
            self._month = datetime_value.month
            self._day = datetime_value.day
            self._hour = datetime_value.hour
            self._minute = datetime_value.minute
            self._second = datetime_value.second
            self._microsecond = datetime_value.microsecond

        if tz_info is None:
            self._tz_info = pytz.utc
        else:
            self._tz_info = tz_info

    def from_datetime_part(self, year, month, day, hour, minute, second, microsecond):
        self._year = year
        self._month = month
        self._day = day
        self._hour = hour
        self._minute = minute
        self._second = second
        self._microsecond = microsecond

    def to_string(self, fmt, tz=pytz.utc):
        return datetime.datetime(self._year, self._month, self._day, self._hour, self._minute, self._second,
                                 self._microsecond, tzinfo=tz).strftime(fmt)

    def to_datetime(self, tz=pytz.utc):
        return datetime.datetime(self._year, self._month, self._day, self._hour, self._minute, self._second,
                                 self._microsecond, tzinfo=tz)

    @property
    def tick_split(self):
        date_part = (self._year * 10000) + (self._month * 100) + self._day
        time_part = (self._hour * 10000) + (self._minute * 100) + self._second
        return date_part, time_part, self._microsecond

    @property
    def year(self):
        return self._year

    @property
    def month(self):
        return self._month

    @property
    def day(self):
        return self._day

    @property
    def hour(self):
        return self._hour

    @property
    def minute(self):
        return self._minute

    @property
    def second(self):
        return self._second

    @property
    def microsecond(self):
        return self._microsecond

    @property
    def ticks(self):
        return TimestampConverter.get_ticks(self._year, self._month, self._day, self._hour, self._minute, self._second,
                                            self._microsecond)


class TimestampConverter:
    @staticmethod
    def from_ticks(ticks):
        year = math.floor(ticks // 10000000000000000)
        month = math.floor((ticks // 100000000000000) % 100)
        day = math.floor((ticks // 1000000000000) % 100)
        hour = int((ticks // 10000000000) % 100)
        minute = int((ticks // 100000000) % 100)
        second = int((ticks // 1000000) % 100)
        microsecond = int(ticks % 1000000)
        return Timestamp(year, month, day, hour, minute, second, microsecond)

    @staticmethod
    def from_tick_split(date_part, time_part, microsecond):
        year = math.floor(date_part // 10000)
        month = math.floor((date_part // 100) % 100)
        day = math.floor(date_part % 100)
        hour = int((time_part // 10000) % 100)
        minute = int((time_part // 100) % 100)
        second = int(time_part % 100)
        return Timestamp(year, month, day, hour, minute, second, microsecond)

    @staticmethod
    def get_ticks(year, month, day, hour, minute, second, microsecond):
        return (year * 10000000000000000) + (month * 100000000000000) + (
            day * 1000000000000) + (hour * 10000000000) + (minute * 100000000) + (
                   second * 1000000) + microsecond

    @staticmethod
    def next_minute_ticks(year, month, day, hour, minute, minute_units=1):
        date_time = datetime.datetime(year, month, day, hour, minute, 0, 0, tzinfo=pytz.utc)
        next_minute = date_time + datetime.timedelta(minutes=minute_units)
        return TimestampConverter.to_ticks(next_minute)

    @staticmethod
    def next_hour_ticks(year, month, day, hour, hour_units=1):
        date_time = datetime.datetime(year, month, day, hour, 0, 0, 0, tzinfo=pytz.utc)
        next_hour = date_time + datetime.timedelta(hours=hour_units)
        return TimestampConverter.to_ticks(next_hour)

    @staticmethod
    def next_day_ticks(year, month, day, day_units=1):
        date_time = datetime.datetime(year, month, day, 0, 0, 0, 0, tzinfo=pytz.utc)
        next_day = date_time + datetime.timedelta(days=day_units)
        return TimestampConverter.to_ticks(next_day)

    @staticmethod
    def next_month_ticks(year, month, month_units=1):
        date_time = datetime.datetime(year, month, 1, 0, 0, 0, 0, tzinfo=pytz.utc)
        next_month = date_time + relativedelta.relativedelta(months=month_units)
        return TimestampConverter.to_ticks(next_month)

    @staticmethod
    def to_ticks(datetime_value):
        return TimestampConverter.get_ticks(datetime_value.year, datetime_value.month, datetime_value.day,
                                            datetime_value.hour, datetime_value.minute, datetime_value.second,
                                            datetime_value.microsecond)


class TimestampedItem:
    def __init__(self):
        self._timestamp = None

    def set(self, timestamp):
        self._timestamp = timestamp

    @property
    def timestamp(self):
        return self._timestamp


class TimestampedFloatItem:
    def __init__(self):
        self._timestamp = None
        self._value = None

    def write(self, timestamp, value):
        self._timestamp = timestamp
        self._value = value

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def value(self):
        return self._timestamp
