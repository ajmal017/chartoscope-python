from chartoscope.core.common.tradingsession import *

def test_trading_session_subscription():
    calendar = TradingSession.AllDayAllMarketZoneSession.value
    trading_start = datetime(2017, 8, 23)
    tracker = calendar.generate_schedule(trading_start, trading_start + timedelta(weeks=52))

    def on_day_start_session(zone, stage, notification_timestamp):
        print("session started@{}".format(str(notification_timestamp)))

    def on_day_close_session(zone, stage, notification_timestamp):
        print("session ended@{}".format(str(notification_timestamp)))

    tracker.subscribe(on_day_start_session, MarketSessionStage.Opening, UtcMarketZone.Frankfurt)
    tracker.subscribe(on_day_close_session, MarketSessionStage.Closing, UtcMarketZone.Frankfurt)

    for hours in range(1,24):
        tracker.synchronize(trading_start + timedelta(hours=hours))



