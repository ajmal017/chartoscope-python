#!/usr/bin/env python

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import mpl_finance

def candle_price_ref(price, candle_height):
  #return(int(price/candle_height)*candle_height)
  return(round(price/candle_height)*candle_height)

print("Reading CSV (please wait)")
df = pd.read_csv('test_EURUSD/EURUSD-2012-07.csv', names=['Symbol', 'Date_Time', 'Bid', 'Ask'], index_col=1)
print("End of reading")

df['Bid'] = df['Bid']
#candle_height = 0.0015
#candle_height = 0.0010
#candle_height = 0.0005
candle_height = 0.0001
#candle_height = 0.000001

price = df.ix[0]['Bid']
price_ref = candle_price_ref(price, candle_height)

ID = 0
#print("ID={0} price_ref={1}".format(ID, price_ref))

candle_price_open = []
candle_price_close = []

candle_price_open.append(price) # price ou price_ref
candle_price_close.append(price)

for i in range(len(df)):
  price = df.ix[i]['Bid']
  candle_price_close[ID] = price

  new_price_ref = candle_price_ref(price, candle_height)


  if new_price_ref!=price_ref:
    candle_price_close[ID]=new_price_ref
    price_ref = new_price_ref
    ID += 1
    candle_price_open.append(price_ref)
    candle_price_close.append(price_ref)

IDs=range(ID+1)
volume=np.zeros(ID+1)

a_price_open=np.array(candle_price_open)
a_price_close=np.array(candle_price_close)
b_green_candle = a_price_open < a_price_close
candle_price_low = np.where(b_green_candle, a_price_open, a_price_close)
candle_price_high = np.where(b_green_candle, a_price_close, a_price_open)

DOCHLV=zip(IDs, candle_price_open, candle_price_close, candle_price_high, candle_price_low, volume)

#print(DOCHLV)

fig = plt.figure()
fig.subplots_adjust(bottom=0.1)
ax = fig.add_subplot(211)
df['Bid'].plot()
plt.title("Price graph")
ax = fig.add_subplot(212)
plt.title("Renko chart")
candlestick(ax, DOCHLV, width=0.6, colorup='g', colordown='r', alpha=1.0)
plt.show()