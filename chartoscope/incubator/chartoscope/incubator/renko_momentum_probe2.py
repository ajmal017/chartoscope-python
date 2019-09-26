from chartoscope.core.common import BinaryFileAppender, BinaryFileInfo
from chartoscope.core.library import BidAskFileReader, HmaCalculator
from chartoscope.core.extension import RenkoFileReader
from renkomomentum import *
from tqdm import tqdm
from enum import Enum
import struct


reader = RenkoFileReader('EURUSD_2017_06_R1.renko')

hma_calc = HmaCalculator(180, 1000)

with reader.open():
    renko_progress = tqdm(reader.read_all(), total=reader._file_info.row_count)

    probe_writer = RenkoProbeWriter('EURUSD_2017_06_R1_RENKO.probe')
    probe_writer.open()

    for result in renko_progress:
        hma_value = hma_calc.calculate(result.close)
        roc_value = None
        hma_has_reversed = None
        if hma_value is not None:
            if hma_calc.is_valid_index(7):
                roc_value = (((hma_calc.current - hma_calc[7]) / hma_calc[7]) * 100) * 10000
                hma_has_reversed = (hma_calc[2] < hma_calc.previous and hma_calc.previous > hma_calc.current) or \
                    (hma_calc[2] > hma_calc.previous and hma_calc.previous < hma_calc.current)
                if hma_has_reversed:
                    pass
                probe_writer.append(result.timestamp, result.open, result.close, hma_value, hma_has_reversed, roc_value)

                renko_progress.set_description("timestamp = {0} open = {1} close = {2} hma= {3} reversed = {4} roc= {5}".
                                               format(result.timestamp.to_string("%Y%m%d %H:%M:%S"), result.open,
                                                      result.close, hma_value, hma_has_reversed, roc_value))
probe_writer.close()

