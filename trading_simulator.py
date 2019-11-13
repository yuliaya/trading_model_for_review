from item_journey import ROUTE
from utils.trading_item import TradingItem
from utils.market_state import Market
from typing import List
from inspect import getfullargspec


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

            while item.time == epoch and item.state:  # continue while we go the the next time period or leave platform
                func = ROUTE[item.cur_state]
                args_list = getfullargspec(func).args  # get all method arguments
                args = [{'item': item, 'market': market}[arg] for arg in args_list]
                item = func(*args)

    for item in items:
        print(item)

    print('Cost: %d\n' %sum([item.cost for item in items]))
    print ('Income: %d\n' % sum ([item.income for item in items]))


if __name__ == '__main__':
    market = Market(
        lifetime_period=30,
        platform_interest=0.2,
    )
    run_simulator(market)

