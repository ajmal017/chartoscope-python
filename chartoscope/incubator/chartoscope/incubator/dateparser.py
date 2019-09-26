import datetime

def parseDateTime(val):
    return datetime.datetime(
            int(val[0:4]), # %Y
            int(val[4:6]), # %m
            int(val[6:8]), # %d
            int(val[9:11]), # %H
            int(val[12:14]), # %M
            int(val[15:17]), # %s
            int(val[18:]) * 1000) # %f

print(parseDateTime('20130401 00:00:00.258'))