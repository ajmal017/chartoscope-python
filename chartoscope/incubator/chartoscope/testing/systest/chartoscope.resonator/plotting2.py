import matplotlib.pyplot as plt
import pandas as pd

df= pd.DataFrame([[1, 2], [3, 4], [4, 3], [2, 3]])
fig = plt.figure(figsize=(14,8))
for i in df.columns:
    ax=plt.subplot(2,1,i+1)
    df[[i]].plot(ax=ax)
    print(i)
plt.show()