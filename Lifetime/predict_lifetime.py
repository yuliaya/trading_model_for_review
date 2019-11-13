from typing import Type
from Trading.trading_item import TradingItem
from Trading.market_state import Market

def predict_lifetime(item: Type[TradingItem], market: Type[Market]):
    
    #todo change fictive lifetime value

    if item.time == 0:
        item.lifetime = market.epoch + 10
        item.cur_state = 'predict_lifetime'
    else:
        pass
    
    return item
