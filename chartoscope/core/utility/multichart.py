import matplotlib.pyplot as plt
from chartoscope.core.common import *

class Multichart:
    def __init__(self):
        pass

    @staticmethod
    def plot(chart_item):
        if issubclass(type(chart_item), Indicator):
            chart_item.series().plot()
            plt.show()
        elif issubclass(type(chart_item), PriceChart):
            chart_item.series().plot()
            plt.show()
