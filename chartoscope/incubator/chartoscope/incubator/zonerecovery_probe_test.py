from incubator.zonerecovery_probe import *
from incubator.acme import *

feed= AcmeFeed(AcmeFeed("C:\\Workspace\\AcmeBroker"))
probe = ZoneRecoveryProbe(TickerSymbol('EURUSD',10000), feed)
feed.start(probe)