from collections import namedtuple


TechnicalItem = namedtuple('TechnicalItem', 'ta_function price_bar_lambda value_item_lambda')


class Technicals:
    def __init__(self, price_bar_lambda):
        self._technicals = []
        self._price_bar_lambda = price_bar_lambda

    def register(self, ta_function, value_item_lambda):
        self._technicals.append(TechnicalItem(ta_function, self._price_bar_lambda, value_item_lambda))

    def __getitem__(self, index):
        return self._technicals[index]
