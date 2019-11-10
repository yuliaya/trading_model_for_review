from typing import Type
from Trading.trading_item import TradingItem

def transactional_pricing(item: Type[TradingItem]):

    user = item.owner

    #todo check to real transacional pricing algo
    if user.segment == 'trader':
        item.price_transactional = .8 * item.price_real
    else:
        item.price_transactional = .6 * item.price_real
    item.cur_state = 'user_selling_decision'