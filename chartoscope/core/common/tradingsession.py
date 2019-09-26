from enum import Enum
from datetime import datetime, timedelta
from chartoscope.core.common.marketsession import  UtcMarketZone


class MarketSessionStage(Enum):
    Opening = 1
    Closing = 2

class TradingSessionNotifier:
    def  __init__(self):
        self._subscribers = []
        self._zones = [{"zone": UtcMarketZone.Frankfurt, "has_opened": False, "has_closed": True}]

    def subscribe(self, notification_lambda, session_stage, session_zone):
        self._subscribers.append({"notification_lambda": notification_lambda, "session_zone": session_zone, "session_stage": session_stage})

    def synchronize(self, current_date_time):
        for subscriber in self._subscribers:
            for zone in self._zones:
                if zone["zone"]==subscriber["session_zone"]:
                    within_session = subscriber["session_zone"].value.within_session(current_date_time)
                    if subscriber["session_stage"]==MarketSessionStage.Opening and within_session:
                        if zone["has_closed"] and not zone["has_opened"]:
                            subscriber["notification_lambda"](subscriber["session_zone"], subscriber["session_stage"], current_date_time)
                            zone["has_opened"] = True
                            zone["has_closed"] = False
                    elif not within_session and subscriber["session_stage"] == MarketSessionStage.Closing and zone["has_opened"] and not zone["has_closed"]:
                            subscriber["notification_lambda"](subscriber["session_zone"], subscriber["session_stage"], current_date_time)
                            zone["has_opened"] = False
                            zone["has_closed"] = True


class TradingSessionCalendar:
    def __init__(self, plan_name, market_zones):
        self._plan_name = plan_name
        self._market_zones = market_zones

    def generate_schedule(self, start_datetime, end_date_time=None, years=0, months=0):
        schedule = []
        hourly_interval= datetime(start_datetime.year, start_datetime.month, start_datetime.day, start_datetime.hour, 0, 0, 0)

        while hourly_interval < end_date_time:
            hourly_interval+= timedelta(hours=1)
        return TradingSessionNotifier()


class TradingSession(Enum):
    AllDayAllMarketZoneSession = TradingSessionCalendar("AllDayAllMarketZones", UtcMarketZone.AllMarketZones)
    EurAsianZoneSession = TradingSessionCalendar("EurAsianZonePlan", UtcMarketZone.EuropeanAsianZones)
    EurUsZoneSession = TradingSessionCalendar("EurUsZonePlan", UtcMarketZone.EuropeanAmericanZones)