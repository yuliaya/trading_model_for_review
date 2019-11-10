from typing import Type
from Trading.trading_item import TradingItem


def future_price(item: Type[TradingItem]):

    # todo change fictive current and future prices
    item.price_real = 80.
    item.price_predicted = 100.

    item.cur_state = 'future_price'

    return item