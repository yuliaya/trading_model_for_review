from utils.market_state import Market
from utils.create_new_items import create_items,initiate_items_list
import os
import pandas as pd
from datetime import timedelta, datetime
from predict_demand.predict_future_demand import initial_demand_predict, daily_demand_predict
from decision_making.market_engine import trading_algo
from math import isnan

def run_simulator(market: Market) -> pd.DataFrame:

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
        if len([item for item in market.items if isnan(item.price)]):
            pass
        market = daily_demand_predict(market)
        market = trading_algo(market)
        if len([item for item in market.items if isnan(item.price)]):
            pass
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
    return output_df

    # outpout_df = pd.DataFrame()
    # for brand in market.all_models:
    #     print(brand)
    #     print(market.demand_models[brand]['best_model']['model'])
    #     print(market.demand_predictions_expected[brand])
    #     print(market.demand_30d_predictions_expected[brand])
    #     s = pd.Series([market.demand_predictions_expected[brand][period] for period in
    #                   sorted(market.demand_predictions_expected[brand].keys())],
    #                   index=sorted(market.demand_predictions_expected[brand].keys()))
    #     outpout_df['%s_daily_demand' % brand] = s
    #     s2 = pd.Series([market.demand_30d_predictions_expected[brand][period] for period in
    #                     sorted(market.demand_30d_predictions_expected[brand].keys())],
    #                     index=sorted(market.demand_30d_predictions_expected[brand].keys()))
    #     outpout_df['%s_30d_demand' % brand] = s2
    #     s3 = pd.Series([market.demand_predictions_real[brand][period] for period in
    #                   sorted(market.demand_predictions_real[brand].keys())],
    #                   index=sorted(market.demand_predictions_real[brand].keys()))
    #     outpout_df['%s_daily_demand_real' % brand] = s3
    #     s4 = pd.Series([market.demand_30d_predictions_real[brand][period] for period in
    #                     sorted(market.demand_30d_predictions_real[brand].keys())],
    #                     index=sorted(market.demand_30d_predictions_real[brand].keys()))
    #     outpout_df['%s_30d_demand_real' % brand] = s4
    # outpout_df.to_csv('demand_predictions.csv')\


if __name__ == '__main__':

    _ = {
        "lifetime_period": 250,
        "platform_interest": 0.2,
        "invest": False,
        "decision_threshold": 1,
        "segmentation": False,
        "segments": {'general': {'p': 0.4,'reduce_math_exp': 0.6},
                     'trader': {'p': 0.3,'reduce_math_exp': 0},
                     'poor': {'p': 0.3, 'reduce_math_exp': 0.8}
                  },
        "lifetime_accuracy": None,
        "demand_rmse_to_avg": None,
        "min_margin": 500,
        "max_margin": 1000}

    parameters_list = []
    if _['invest']:
        parameters_list.append("inv")
    if _['segmentation']:
        parameters_list.append("segm")
    parameters_list.append("dec_t=%s" %_['decision_threshold'])
    parameters_list.append("life_acc=%s" % _['lifetime_accuracy'])
    parameters_list.append("demand_rmse=%s" % _['demand_rmse_to_avg'])
    parameters_list.append("min_m=%s" % _['min_margin'])
    parameters_list.append("max_m=%s" % _['max_margin'])
    parameters_list.append(str(datetime.now().date()))
    dir = 'results/' + (' '.join(parameters_list))

    os.mkdir(dir)

    for iteration in range(13, 100):
        market = Market(**_)
        df = run_simulator(market)
        df.to_csv(dir + "/%s.csv" % iteration)

