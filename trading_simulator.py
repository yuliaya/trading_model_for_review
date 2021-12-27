from utils.market_state import Market
from utils.create_new_items import create_items,initiate_items_list
from utils.aws import post_to_s3
import os
import pandas as pd
from datetime import timedelta, datetime
from predict_demand.predict_future_demand import initial_demand_predict, daily_demand_predict
from decision_making.market_engine import trading_algo
from math import isnan

PARAMS = {
    "lifetime_period": 250,
    "platform_interest": 0.2,
    "invest": True,
    "segmentation": False,
    "segments": {'general': {'p': 0.4, 'reduce_math_exp': 0.6},
                 'trader': {'p': 0.3, 'reduce_math_exp': 0},
                 'poor': {'p': 0.3, 'reduce_math_exp': 0.8}
                 },
    "lifetime_accuracy": 0.7,
    "demand_rmse_to_avg": 0.7,
    "min_margin": 500,
    "max_margin": 1000,
    'num_epochs': 1}

def run_simulator(market: Market) -> pd.DataFrame:

    market = initiate_items_list(market)
    # market.stat_on_items()
    market = initial_demand_predict(market)

    income_list = []
    cost_list = []
    profit_list = []
    while market.epoch <= market.lifetime_period:
        # print('Current date: %s' % market.cur_date)
        # print('Epoch: %s' % market.epoch)
        market.update_median_prices()
        market = create_items(market)
        market = daily_demand_predict(market)
        market = trading_algo(market)
        income = sum([item.income for item in market.items if item.cur_time_period >= 0])
        income_list.append(income)
        cost = sum([item.cost for item in market.items])
        cost_list.append(cost)
        profit = income - cost
        profit_list.append(profit)
        # print('Incomes: %s' % income)
        # print('Cost: %s' % cost)
        # print('Profit: %s' % profit)
        # print('Sold today: %s' % len([item for item in market.items if item.cur_time_period == market.epoch and
        #                               not item.state and item.income > 0]))
        # print('Left today: %s' % len([item for item in market.items if item.cur_time_period == market.epoch and
        #                               not item.state and item.income == 0]))
        market.epoch += 1
        market.cur_date = market.cur_date + timedelta(days=1)

    output_df = pd.DataFrame({'incomes': income_list, 'costs': cost_list, 'profit': profit_list})
    return output_df


def run(params: dict):
    market = Market(**params)
    df = run_simulator(market)
    return df


if __name__ == '__main__':
    run(PARAMS)