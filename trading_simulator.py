from item_journey import ROUTE
from Trading.trading_item import TradingItem
from Trading.market_state import Market
from typing import Type

def create_items(epoch, amount: int=0):
    return [TradingItem(t=epoch)] * amount

def run_simulator(market: Type[Market])

    items = []

    for epoch in range(market.life_period):
        if epoch == 0:
            items.append(create_items(1))
        else:
            items.append(create_items(0))


if __name__ == '__main__':
    market = Market(
        life_period=30,
        platform_interest=0.2,
    )

    run_simulator(market)

