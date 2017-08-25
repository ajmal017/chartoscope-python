from lookbehindpool import *

class Sma:
        def __init__(self, period):        
                self._value_pool = LookBehindPool(period, lambda: None)
                self._period = period

        def calculate(self, value):
                complex(value) # validate int, long, float or complex value
                
                self._value_pool.assign(value)
                if self._value_pool.length >= self._period:
                        sma_value = sum(self._value_pool.read_back()) / self._period            

                        return sma_value
                else:
                        return None

        def calculate_batch(self, value_list):
                return [self.calculate(value) for value in value_list]

        @property
        def is_primed(self):
                return self._value_pool.length >= self._period - 1
        
        def calculate_primer(self, *args):
                if self.is_primed:
                        raise Exception("Primer calculation is already completed")

                priming_remaining = self._period - self._value_pool.length -1
                if len(args) >= priming_level:
                        raise Exception("The number of values exceed the required primer calculation limit of {0}.  Only {1} values are needed to complete priming".format(self._period, priming_remaining))
                else:
                        for value in args:
                                self.calculate(value)
                        return self.is_primed

        @property
        def period(self):
                return self._period
