from item_journey import ROUTE
from Trading.trading_item import TradingItem
from Trading.market_state import Market
from typing import List


def create_items(epoch, amount: int=0):
    return [TradingItem(time=epoch)] * amount



def run_simulator(market: Market):

    items: List[TradingItem] = []

    for epoch in range(market.lifetime_period):
        if epoch == 0:
            items.extend(create_items(epoch, 2))
        else:
            items.extend(create_items(epoch))

        for item in items:
            print(type(item))
            while item.time == 0:  # continue while we go the the next time period
                func = ROUTE[item.cur_state]
                args_list = func.__code__.co_varnames
                args = [{'item': item, 'market': market}[arg] for arg in args_list]
                item = func(*args)

    for item in items:
        print(item)


if __name__ == '__main__':
    market = Market(
        lifetime_period=30,
        platform_interest=0.2,
    )

    run_simulator(market)

