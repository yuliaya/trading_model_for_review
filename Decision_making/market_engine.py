from typing import Type
from Trading.trading_item import TradingItem

def trading_algo(item: Type[TradingItem]):

    if item.lifetime < item.time:
        item.time += 1
