from chartoscope.core.common import *


utc_datetime= datetime(2017, 8, 22, 0, 0, 0, tzinfo=MarketTimezone.Utc.value)
print(UtcMarketZone.get_market_zones(utc_datetime))
#print(utc_datetime.astimezone(MarketTimezone.Frankfurt.value))