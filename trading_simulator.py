from item_journey import ROUTE
from utils.trading_item import TradingItem
from utils.market_state import Market
from typing import List
from inspect import getfullargspec


def create_items(epoch, amount: int=0):  # todo real item parameters based on stats
    '''

    :param epoch:
    :param amount:
    :return:

    this function generates items based on market expectations re number of new items and their characteristics
    '''
    return [TradingItem(time_created=epoch)] * amount


def run_simulator(market: Market):

    items: List[TradingItem] = []

    for epoch in range(market.lifetime_period):
        if epoch == 0:
            items.extend(create_items(epoch, 2))  # todo correct number of new items based on stats from sales

        for item in items:

            while item.cur_time == epoch and item.state:  # continue while we go the the next time period or leave platform
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

