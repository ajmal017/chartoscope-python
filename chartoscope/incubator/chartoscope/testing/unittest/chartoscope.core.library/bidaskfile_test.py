import tempfile

def test_write():
        fileName= createFile()
        assert(True)

def createFile():
    tempFile = tempfile.mktemp()
    print(tempFile)
    appender = BidAskFileAppender(tempFile)
    appender.open()
    timestamp = Timestamp(2017, 4, 3, 5, 2, 1, 123213)
    for x in range(1, 100):
        appender.append(timestamp, 1, 2)
    appender.close()
    return tempFile

def read():
    tempFile = tempfile.mktemp()
    reader = BidAskFileReader(tempFile)
    reader.open()

    for x in range(1, 1000000):
        result= reader.read()
        #print(result)

    reader.close()
    assert (True)
