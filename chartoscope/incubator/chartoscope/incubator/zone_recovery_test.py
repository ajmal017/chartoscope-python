from incubator.zonerecovery import *
from incubator.acme import *

def test_backtest():
    backtestProfile= Backtest.execute(ZoneRecovery(TickerSymbol('EURUSD'), AcmeBroker(AcmeFeed("C:\\Workspace\\AcmeBroker"))))
    assert(backtestProfile!=None)