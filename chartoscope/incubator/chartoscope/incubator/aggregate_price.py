#!/usr/bin/env python
from chartoscope.core.common import *
from chartoscope.core.library import *
from chartoscope.core.extension import *
import sys
from tqdm import tqdm

def append(ohlc, currentPriceBar):
    ohlc.append(currentPriceBar.timestamp, currentPriceBar.open, currentPriceBar.high, currentPriceBar.low, currentPriceBar.close)

def appendProbe(probe, currentProbeItem):
    probe.append(currentProbeItem.timestamp, currentProbeItem.value)

def appendRenko(renko, currentPriceBar):
    renko.append(currentPriceBar.timestamp, currentPriceBar.open, currentPriceBar.close)


# ohlcWriterM1= OhlcFileAppender('EURUSD_2013_04_M1.ohlc')
# ohlcWriterM1.open()
# ohlcM1= Ohlc(TimeframeInterval.M1, lambda currentPrice, priceHistory: append(ohlcWriterM1, currentPrice))
#
# ohlcWriterM5= OhlcFileAppender('EURUSD_2013_04_M5.ohlc')
# ohlcWriterM5.open()
# ohlcM5= Ohlc(TimeframeInterval.M5, lambda currentPrice, priceHistory: append(ohlcWriterM5, currentPrice))
#
# ohlcWriterM10= OhlcFileAppender('EURUSD_2013_04_M10.ohlc')
# ohlcWriterM10.open()
# ohlcM10= Ohlc(TimeframeInterval.M10, lambda currentPrice, priceHistory: append(ohlcWriterM10, currentPrice))
#
# ohlcWriterH4= OhlcFileAppender('EURUSD_2013_04_H4.ohlc')
# ohlcWriterH4.open()
# ohlcH4= Ohlc(TimeframeInterval.H4, lambda currentPrice, priceHistory: append(ohlcWriterH4, currentPrice))
#
# ohlcWriterD1= OhlcFileAppender('EURUSD_2013_04_D1.ohlc')
# ohlcWriterD1.open()
# ohlcD1= Ohlc(TimeframeInterval.D1, lambda currentPrice, priceHistory: append(ohlcWriterD1, currentPrice))
#
# haWriterH4= HeikenAshiFileAppender('EURUSD_2013_04_H4.heikenashi')
# haWriterH4.open()
# haH4= HeikenAshi(TimeframeInterval.H4, lambda currentPrice, priceHistory: append(haWriterH4, currentPrice))

# haWriterM30Ema= EmaFileAppender('EURUSD_2013_04_M30.ema')
# haWriterM30Ema.open()
# ema= EmaProbe(20, lambda currentValue, valueHistory: appendProbe(haWriterM30Ema, currentValue))

# haWriterM30= HeikenAshiFileAppender('EURUSD_2013_04_M30.heikenashi')
# haWriterM30.open()
# haM30= HeikenAshi(TimeframeInterval.M30, lambda currentPrice, priceHistory: append(haWriterM30, currentPrice))
# haM30.probes.register(ema, lambda heikenAshiBar: heikenAshiBar.close)

renkoWriterR10= RenkoFileAppender('EURUSD_2017_06_R1.renko')
renkoWriterR10.open()
renkoR10= Renko(FeedInterval(RangeInterval.R1), 10000, lambda currentPrice, priceHistory: appendRenko(renkoWriterR10, currentPrice))
#hma_200 = HmaIndicator(200)
#renkoR10.technicals.register(hma_200, lambda renko_bar: renko_bar.close)

reader = BidAskFileReader('EURUSD_2017_06.bidask')
with reader.open():
    for result in tqdm(reader.read_all(), total=reader._file_info.row_count):
        # ohlcM1.priceAction(result[0], result[1], result[2])
        # ohlcM5.priceAction(result[0], result[1], result[2])
        # ohlcM10.priceAction(result[0], result[1], result[2])
        # ohlcH4.priceAction(result[0], result[1], result[2])
        # ohlcD1.priceAction(result[0], result[1], result[2])
        # haH4.priceAction(result[0], result[1], result[2])
        renkoR10.price_action(result[0], result[1], result[2])

reader.close()
# ohlcWriterM1.close()
# ohlcWriterM5.close()
# ohlcWriterM10.close()
# ohlcWriterH4.close()
# ohlcWriterD1.close()
# haWriterH4.close()
renkoWriterR10.close()
#haWriterM30Ema.close()