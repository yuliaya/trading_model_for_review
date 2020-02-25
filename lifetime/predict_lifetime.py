from typing import Type
from utils.trading_item import TradingItem
from utils.market_state import Market

def predict_lifetime(item: Type[TradingItem], market: Type[Market]):
    
    #todo change fictive lifetime value

    if item.cur_time == 0:
        item.lifetime = 10
        item.cur_state = 'predict_lifetime'
    else:
        pass
    
    return item
