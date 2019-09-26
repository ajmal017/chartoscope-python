from incubator.zonerecovery import *
from incubator.acme import *

backtestProfile= Backtest.execute(ZoneRecovery(TickerSymbol('EURUSD',10000), AcmeBroker(AcmeFeed("C:\\Workspace\\AcmeBroker"))))


