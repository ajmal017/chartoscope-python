from chartoscope.core.common import *
from chartoscope.core.library import *

class Backtest:
    def __init__(self):
        pass

    @staticmethod
    def plot(chartoscope_app, feeder):
        appType= chartoscope_app.__class__.__bases__[0]
        if appType is ExpertAdvisor:
            print('Plotting expert advisor application')
        elif appType is SignalAdvisor:
            print('Plotting signal advisor application')
        elif appType is Probe:
            print('Plotting probe application')
        elif appType is PriceAction:
            print('Plotting price action application')
            feeder.start(chartoscope_app)

    @staticmethod
    def execute(chartoscope_app):
        appType = chartoscope_app.__class__.__bases__[0]
        if appType is ExpertAdvisor:
            #print('Running expert advisor application')
            chartoscope_app._broker.dataFeed.start(chartoscope_app)
            #wait for synchronous operation to complete
            return chartoscope_app._broker.getExecutionProfile()
        elif appType is SignalAdvisor:
            print('Running signal advisor application')
        elif appType is Probe:
            print('Running probe application')
        elif appType is PriceAction:
            print('Running price action application')
