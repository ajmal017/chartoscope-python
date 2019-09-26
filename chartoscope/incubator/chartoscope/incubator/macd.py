import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt
from chartoscope.core.extension.probe import *

ema= EmaIndicator(20)
emaReader= EmaFileReader("")
ema.evaluate()

names = ['FB']
def get_px(stock, start, end):
     return pdr.get_data_yahoo(stock, start, end)['Adj Close']

result= get_px(names[0], '1/1/2016', '1/17/2017')
print(result.index[0])

px = pd.DataFrame({n: get_px(n, '1/1/2016', '1/17/2017') for n in names})
px['26 ema'] = pd.ewma(px["FB"], span=26)
px['12 ema'] = pd.ewma(px["FB"], span=12)
px['MACD'] = (px['12 ema'] - px['26 ema'])
px.plot(y= ['FB'], title='FB')
px.plot(y= ['MACD'], title='MACD')

#plt.show()