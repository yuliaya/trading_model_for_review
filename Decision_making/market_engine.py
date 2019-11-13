from typing import Type
from utils.trading_item import TradingItem
from utils.market_state import Market
from Lifetime.predict_lifetime import predict_lifetime

def trading_algo(item: Type[TradingItem], market: Type[Market]):

    #todo real algorithm

    if item.lifetime < item.time:
        item.time += 1
        item.likes += 1
        new_lifetime = predict_lifetime(item, market)
        if new_lifetime != item.lifetime:
            item.price_predicted = predict_lifetime(item, market)

    else:
        item.state = False
        item.cur_state = 'sold'
        if item.possession == 'user':
            item.income = item.price_supply * market.platform_interest
        else:
            item.income = item.price_supply

    return item

