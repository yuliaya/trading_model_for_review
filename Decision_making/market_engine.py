from typing import Type
from Trading.trading_item import TradingItem
from Trading.market_state import Market

def trading_algo(item: Type[TradingItem], market: Type[Market]):

    if item.lifetime < item.t:
        item.t += 1
