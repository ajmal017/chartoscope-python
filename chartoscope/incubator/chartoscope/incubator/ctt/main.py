import argparse
import datetime as dt
import os

def back_test_mode(feed_file):
    pass

parser = argparse.ArgumentParser()
parser.add_argument('--mode', help='Run mode')
parser.add_argument('--feed', help='Backtest feed file')
parser.add_argument('--ccpl', help='Correlated currency pair list')

major_version_no = 0
minor_version_no= 1

print("Correlative Trend Trading v{}.{}".format(major_version_no, minor_version_no))

args = parser.parse_args()

start_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

if (args.mode is None):
    # Run in Backtest by default
    mode = "bt"
    ccpl = "EURUSDGBP"
    feed_file = "EURUSDGBP-2017-08-2016-08.feed"
else:
    mode = str.lower(args.mode)
    ccpl = str.upper(args.ccpl)
    feed_file = args.feed

if (mode == "bt"):
    print("Entering Backtest mode @{}".format(start_time))

    if (os.path.isfile(feed_file)):
        back_test_mode(ccpl, feed_file)
    else:
        print("Feed file '{}' does not exist.".format(feed_file))

    end_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    print("Leaving Backtest mode @{}".format(end_time))