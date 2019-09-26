from incubator.renko_momentum_probe import *
from incubator.acme import *

feed= AcmeFeed(AcmeFeed("C:\\Workspace\\AcmeBroker"))
probe = RenkoMomentumProbe(TickerSymbol('EURUSD',10000), feed)
feed.start(probe)