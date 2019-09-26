from enum import Enum

class EventOption(Enum):
    Nothing = 0
    Tick = 1
    PriceAction = 2
    Signal = 3