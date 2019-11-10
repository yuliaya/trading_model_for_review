from typing import Type
from Trading.trading_item import TradingItem
from Trading.market_state import Market

def check_invest_interest(item: Type[TradingItem], market: Type[Market]):

    if item.price_real < item.price_predicted:
        item.cur_state = 'user_decision'
    else:
        item.cur_state = 'transactional_pricing'

def user_decision(item: Type[TradingItem]):

    user = item.owner

    #todo change fictive decision engine for a user
    user.selling_decision = True

def check_if_worth_selling(item: Type[TradingItem]):
    user = item.owner
    if user.min_price > item.price_transactional:
        item.cur_state = 'user_decision'
    else:
        item.cost = item.price_transactional
        item.possession = 'platform'
        item.cur_state = 'trading'
