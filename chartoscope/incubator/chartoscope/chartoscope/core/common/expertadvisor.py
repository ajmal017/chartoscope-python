from chartoscope.core.common import *


class ExpertAdvisor:
    def __init__(self, broker):
        self._broker = broker
        self._feeder = None

    def start(self):
        self._feeder.back_fill()
        self._feeder.activate()

    def stop(self):
        pass

    def react(self, events):
        if events.contains(EventOption.Signal):
            self.on_signal()
        if events.contains(EventOption.PriceAction):
            self.on_price_action()
        if events.contains(EventOption.Tick):
            self.on_tick()

    def back_fill(self):
        pass

    def on_signal(self):
        pass

    def on_price_action(self):
        pass

    def on_tick(self):
        pass
