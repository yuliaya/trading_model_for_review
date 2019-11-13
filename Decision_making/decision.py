from typing import Type
from Trading.trading_item import TradingItem
from Trading.market_state import Market

def check_invest_interest(item: Type[TradingItem], market: Type[Market]):

    # if future price is expected to grow - the platform decides to buy the item

    if item.price_market < item.price_predicted:
        item.cur_state = 'user_decision'
    else:
        item.cur_state = 'transactional_pricing'
    return item

def user_decision(item: Type[TradingItem]):

    # user decides whether he wants to continue and sell the item or leave the platform
    user = item.owner

    # todo change fictive decision engine for a user + define market price
    if True:
        user.selling_decision = True
        item.cur_state = 'trading'
        item.price_supply = 80.
    else:
        item.cur_state = 'left_market'
        item.state = False
    return item

def check_if_worth_selling(item: Type[TradingItem]):

    # the owner considers whether suggested item price is okay or he wants to continue selling on his own

    user = item.owner
    if user.min_price > item.price_transactional:
        item.cur_state = 'user_decision'
    else:
        item.cost = item.price_transactional
        item.possession = 'platform'
        item.cur_state = 'trading'
    return item
