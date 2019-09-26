import datetime

from chartoscope.core.common import Timestamp


def test_timestamp_to_number():
    timestamp= Timestamp(2017, 4, 3, 5, 2, 1, 123213)
    result = timestamp.ticks
    assert(result == 20170403050201123213)

def test_timestamp():
    timestamp= Timestamp(datetime_value= datetime.datetime.now())
    result= timestamp.ticks
    print(str(result))
    assert(result > 0)


def test_tickSplit():
    timestamp = Timestamp(2017, 4, 3, 5, 2, 1, 123213)
    result = timestamp.tick_split
    assert(result[0]==20170403)
    assert(result[1] == 50201)
    assert(result[2]==123213)
    newTimeStamp= Timestamp.from_tick_split(result[0], result[1], result[2])
    assert(newTimeStamp.ticks==timestamp.ticks)