from typing import Type
from Trading.trading_item import TradingItem
from Trading.market_state import Market

def trading_algo(item: Type[TradingItem], market: Type[Market]):

    if item.lifetime < item.time:
        item.time += 1


    else:
        item.state = False
        item.cur_state = 'sold'
        if item.possession == 'user':
            item.income = item.price_supply * market.platform_interest
        else:
            item.income = item.price_supply

