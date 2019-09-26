from datetime import datetime, timedelta
from pytz import timezone
from enum import Enum


class MarketTimezone(Enum):
    Utc = timezone('UTC')
    Frankfurt = timezone('Europe/Berlin')
    London = timezone('Europe/London')

class UtcMarketSession:
    def __init__(self, name, opening, closing):
        self._name = name
        self._opening = opening
        self._current_day_opening = datetime.strptime(opening, "%I:%M %p")
        self._closing = closing
        self._current_day_closing = datetime.strptime(closing, "%I:%M %p")
        self.start_of_day = datetime.strptime("12:00 AM", "%I:%M %p")
        if self._current_day_closing < self._current_day_opening:
            self._next_day_closing = self._current_day_closing
            self._current_day_closing = self.start_of_day + timedelta(days=1)
        else:
            self._next_day_closing= None

    def within_session(self, utc_date_time):
        input_time = datetime( self.start_of_day.year,  self.start_of_day.month,  self.start_of_day.day,
                               utc_date_time.hour, utc_date_time.minute, utc_date_time.second, utc_date_time.microsecond)
        if self._next_day_closing is None:
            pass
        return (input_time >= self._current_day_opening and input_time < self._current_day_closing) or \
               (self._next_day_closing is not None and input_time >= self.start_of_day and input_time < self._next_day_closing)

    def next_opening_session(self, init_timestamp):
        utc_date_time = init_timestamp.to_datetime()
        input_day = datetime(utc_date_time.year, utc_date_time.month, utc_date_time.day)
        input_time = datetime(self.start_of_day.year, self.start_of_day.month, self.start_of_day.day,
                              utc_date_time.hour, utc_date_time.minute, utc_date_time.second, utc_date_time.microsecond)

        if input_time > self._current_day_opening:
            opening_session = datetime.combine(input_day, self._current_day_opening.time()).astimezone(init_timestamp._tz_info)
        else:
            opening_session = datetime.combine(utc_date_time + timedelta(days=1), self._current_day_opening.time()).astimezone(init_timestamp._tz_info)

        if opening_session.weekday()==5:
            return opening_session + timedelta(days=2)
        else:
            return opening_session

    def __repr__(self):
        return self._name


class UtcMarketZone(Enum):
    Frankfurt = UtcMarketSession("Frankfurt", "06:00 AM", "02:00 PM")
    London = UtcMarketSession("London", "07:00 AM", "03:00 PM")
    NewYork = UtcMarketSession("NewYork", "12:00 PM", "08:00 PM")
    Sydney = UtcMarketSession("Sydney", "10:00 PM", "06:00 AM")
    Tokyo = UtcMarketSession("Tokyo", "11:00 PM", "07:00 AM")

    AllMarketZones = [Frankfurt, London, NewYork, Sydney, Tokyo]
    EuropeanZones = [Frankfurt, London]
    AmericanZone = [NewYork]
    EuropeanAmericanZones= [Frankfurt, London, NewYork]
    AsianZone = [Sydney, Tokyo]
    EuropeanAsianZones = [Frankfurt, London, Sydney, Tokyo]

    @staticmethod
    def get_market_zones(utc_date_time):
        market_zones = []
        for market_zone in UtcMarketZone.AllMarketZones.value:
            if market_zone.within_session(utc_date_time):
                market_zones.append(market_zone)

        return market_zones