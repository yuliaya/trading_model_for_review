from utils.market_state import Market
from datetime import timedelta
import numpy as np
import pandas as pd


def predict_demand(market: Market, brand: str, delta: int) -> (int, int):
    models = market.demand_models[brand]
    best_model = models['best_model']['model'].split("_")[0]
    features_dict = {}
    for search in market.search_trends[brand].keys():
        features_dict['%s_0' % search] = market.search_trends[brand][search][market.cur_date +
                                                                             timedelta(days=delta)]
        features_dict['%s_7' % search] = market.search_trends[brand][search][market.cur_date +
                                                                             timedelta(days=delta - 7)]
        features_dict['%s_14' % search] = market.search_trends[brand][search][market.cur_date +
                                                                              timedelta(days=delta - 14)]
    features_dict['supply_7'] = len([item for item in market.items if delta - 7 <= item.time_created_period < delta and
                                     item.brand == brand])
    if len([item.price for item in market.items if delta - 7 <= item.time_created_period < delta
                                                   and item.brand == brand]) > 0:
        features_dict['supply_7_prices'] = np.mean([item.price for item in market.items if
                                                    delta - 7 <= item.time_created_period < delta
                                                    and item.brand == brand])
    else:
        features_dict['supply_7_prices'] = 0
    demand_basic = [item for item in market.items if item.brand == brand and
                    delta - 14 <= item.cur_time_period < delta - 7 and not item.state and item.income > 0]
    demand_current = [item for item in market.items if item.brand == brand and
                      delta - 7 <= item.cur_time_period < delta and not item.state and item.income > 0]
    features_dict['demand_7'] = len(demand_current)
    features_dict['demand_7_trend'] = len(demand_current) / len(demand_basic) if len(demand_basic) > 0 else 0
    features_dict['const'] = 1

    if best_model in {'xgbr', 'ensemble'}:
        xgbr_df = pd.DataFrame({feature: [features_dict[feature]] for feature in models['xgbr']['features']})
        xgbr_pred = models['xgbr']['spec'].predict(xgbr_df)[0]

    if best_model in {'mlr', 'ensemble'}:
        mlr_df = pd.DataFrame({feature: [features_dict.get(feature)] for feature in models['mlr']['features']})
        mlr_pred = models['mlr']['spec'].predict(mlr_df)[0]

    if best_model in {'pls', 'ensemble'}:
        pls_df = pd.DataFrame({feature: [features_dict.get(feature)] for feature in models['pls']['features']})
        pls_pred = models['pls']['spec'].predict(pls_df)[0][0]

    error = np.random.normal(0, models['best_model']['rmse'])

    if best_model == 'xgbr':
        return round(xgbr_pred, 0), round(xgbr_pred + error, 0)
    elif best_model == 'mlr':
        return round(mlr_pred, 0), round(mlr_pred + error, 0)
    elif best_model == 'pls':
        return round(pls_pred, 0), round(pls_pred + error, 0)
    elif best_model == 'ensemble':
        return round((xgbr_pred + mlr_pred + pls_pred) / 3, 0),\
               round((xgbr_pred + mlr_pred + pls_pred) / 3 + error, 0)


def initial_demand_predict(market: Market):
    for epoch in range(-45, 0):
        for brand in market.all_models:
            market.demand_predictions_real[brand][epoch] = len(
                [item for item in market.items if item.brand == brand and
                 item.cur_time_period == epoch and item.income > 0 and
                 not item.state])
            market.demand_predictions_expected[brand][epoch] = market.demand_predictions_real[brand][epoch]

    for epoch in range(-45, -30):
        for brand in market.all_models:
            brand_dict = market.demand_predictions_real[brand]
            market.demand_30d_predictions_real[brand][epoch] = sum(
                [brand_dict[e] for e in range(epoch + 1, epoch + 31)])
            market.demand_30d_predictions_expected[brand][epoch] = market.demand_30d_predictions_real[brand][epoch]


    if market.demand_rmse_to_avg is not None:
        for brand in market.all_models:
            avg = np.mean(list(market.demand_30d_predictions_real[brand].values()))
            market.demand_models[brand]['best_model']['rmse'] = avg * market.demand_rmse_to_avg

    for epoch in range(-30, 0):
        for brand in market.all_models:
            predicted_demand, real_demand = predict_demand(market, brand, epoch)
            market.demand_30d_predictions_expected[brand][epoch] = predicted_demand
            market.demand_30d_predictions_real[brand][epoch] = real_demand
            sum_29_real = sum([market.demand_predictions_real[brand][e] for e in range (epoch + 1, epoch + 30)])
            sum_29_expected = sum(
                [market.demand_predictions_expected[brand][e] for e in range(epoch + 1, epoch + 30)])

            if sum_29_real <= market.demand_30d_predictions_real[brand][epoch]:
                market.demand_predictions_real[brand][epoch + 30] = \
                    market.demand_30d_predictions_real[brand][epoch] - sum_29_real
            else:
                market.demand_predictions_real[brand][epoch + 30] = 0

            if sum_29_expected <= market.demand_30d_predictions_expected[brand][epoch]:
                market.demand_predictions_expected[brand][epoch + 30] = \
                    market.demand_30d_predictions_expected[brand][epoch] - sum_29_expected
            else:
                market.demand_predictions_expected[brand][epoch + 30] = 0
    return market


def daily_demand_predict(market: Market):
    for brand in market.all_models:
        market.demand_30d_predictions_real[brand][market.epoch],\
        market.demand_30d_predictions_expected[brand][market.epoch] =\
            predict_demand(market, brand, 0)

        sum_29_real = sum([market.demand_predictions_real[brand][e] for e
                           in range(market.epoch + 1, market.epoch + 30)])
        if sum_29_real <= market.demand_30d_predictions_real[brand][market.epoch]:
            market.demand_predictions_real[brand][market.epoch + 30] = \
                market.demand_30d_predictions_real[brand][market.epoch] - sum_29_real
        else:
            market.demand_predictions_real[brand][market.epoch + 30] = 0

        sum_29_expected = sum([market.demand_predictions_expected[brand][e] for e
                               in range(market.epoch + 1, market.epoch + 30)])
        if sum_29_expected <= market.demand_30d_predictions_expected[brand][market.epoch]:
            market.demand_predictions_expected[brand][market.epoch + 30] = \
                market.demand_30d_predictions_expected[brand][market.epoch] - sum_29_expected
        else:
            market.demand_predictions_expected[brand][market.epoch + 30] = 0

    return market
