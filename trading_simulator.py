from utils.market_state import Market
from utils.create_new_items import create_items,initiate_items_list
from typing import List
from inspect import getfullargspec
import pandas as pd
from datetime import timedelta
from predict_demand.predict_future_demand import initial_demand_predict, daily_demand_predict
from decision_making.market_engine import trading_algo
from math import isnan

def run_simulator(market: Market):

    # market.lifetime_models = None
    market = initiate_items_list(market)
    market.stat_on_items()
    market = initial_demand_predict(market)
    # for brand in market.all_models:
    #     print(brand)
    #     for period in range(-37, 0):
    #         print('Period %s' %period)
    #         print('created %s' % len([item for item in market.items if item.brand == brand and
    #                                   item.time_created_period == period]))
    #         print('Left %s' % len([item for item in market.items if item.brand == brand and
    #                                item.cur_time_period == period and
    #                               item.state is False and item.income > 0]))
    # print('Market initiated')

    # for brand in market.all_models:
    #     print(market.demand_models[brand]['best_model']['model'])
    #     print(market.demand_predictions[brand])
    #     print (market.demand_30d_predictions[brand])

    income_list = []
    cost_list = []
    profit_list = []
    while market.epoch <= market.lifetime_period:
        print('Current date: %s' % market.cur_date)
        print('Epoch: %s' % market.epoch)
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
        print('Incomes: %s' % income)
        print('Cost: %s' % cost)
        print('Profit: %s' % profit)
        print('Sold today: %s' % len([item for item in market.items if item.cur_time_period == market.epoch and
                                      not item.state and item.income > 0]))
        print('Left today: %s' % len([item for item in market.items if item.cur_time_period == market.epoch and
                                      not item.state and item.income == 0]))
        market.epoch += 1
        market.cur_date = market.cur_date + timedelta(days=1)

    output_df = pd.DataFrame({'incomes': income_list, 'costs': cost_list, 'profit': profit_list})
    output_df.to_csv('simulation_results.csv')
    outpout_df = pd.DataFrame()
    for brand in market.all_models:
        print(brand)
        print(market.demand_models[brand]['best_model']['model'])
        print(market.demand_predictions_expected[brand])
        print(market.demand_30d_predictions_expected[brand])
        s = pd.Series([market.demand_predictions_expected[brand][period] for period in
                      sorted(market.demand_predictions_expected[brand].keys())],
                      index=sorted(market.demand_predictions_expected[brand].keys()))
        outpout_df['%s_daily_demand' % brand] = s
        s2 = pd.Series([market.demand_30d_predictions_expected[brand][period] for period in
                        sorted(market.demand_30d_predictions_expected[brand].keys())],
                        index=sorted(market.demand_30d_predictions_expected[brand].keys()))
        outpout_df['%s_30d_demand' % brand] = s2
    outpout_df.to_csv('demand_predictions_zero_error.csv')


if __name__ == '__main__':
    market = Market(
        lifetime_period=100,
        platform_interest=0.2,
        invest=True
    )
    run_simulator(market)

