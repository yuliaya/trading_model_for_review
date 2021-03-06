from typing import Type
from utils.trading_item import TradingItem
from utils.market_state import Market


def future_price(item: Type[TradingItem], market: Type[Market]):

    # todo change fictive current and future prices
    if item.cur_state == 'predict_lifetime':
        item.price_market = 80.
        item.price_predicted = 100.
    elif item.cur_state == 'trading':
        item.price_supply = 80.
    else:
        print('Cannot support item.cur_state on this step!!!!')
        print(item.cur_state)


    item.cur_state = 'future_price'

    return item