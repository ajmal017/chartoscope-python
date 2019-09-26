import csv
import dateutil.parser
import argparse
from tqdm import tqdm

from chartoscope.core.library import *

parser = argparse.ArgumentParser()
parser.add_argument('--source', help='TrueFx CSV file')
parser.add_argument('--target', help='Bid-Ask file')

args = parser.parse_args()

appender = BidAskFileAppender(args.target)
#appender.open(delayedWriteThreshold=1024 * 1000)
appender.open()

lines = 0
chunkSize= 1024 * 1000
with open(args.source, 'r') as f:
    for chunk in iter(lambda: f.read(chunkSize), ''):
        lines += chunk.count('\n')

def parseDateTime(val):
    return datetime.datetime(
            int(val[0:4]), # %Y
            int(val[4:6]), # %m
            int(val[6:8]), # %d
            int(val[9:11]), # %H
            int(val[12:14]), # %M
            int(val[15:17]), # %s
            int(val[18:]) * 1000) # %f

with open(args.source, 'r') as csvfile:
    spamreader = csv.reader(csvfile)

    for row in tqdm(spamreader, total= lines):
        timestamp = Timestamp(datetime_value= parseDateTime(row[1]))
        bid = float(row[2])
        ask = float(row[3])
        appender.append(timestamp, bid, ask)

appender.close()