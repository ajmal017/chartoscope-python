from chartoscope.core.common import *


@Singleton
class PoolConfig:
    DefaultPoolSize = 100
    DefaultCalculatorPoolSize = 100
    DefaultIndicatorPoolSize = 100
    DefaultPriceChartPoolSize = 100

    def __init__(self):
        self._pool_size_config = {}

    def get_pool_size(self, pool_type):
        if pool_type in self._pool_size_config:
            return self._pool_size_config[pool_type]
        else:
            return PoolConfig.DefaultPoolSize

    def set_pool_size(self, object_type, pool_size):
        self._pool_size_config.update({object_type: pool_size})
