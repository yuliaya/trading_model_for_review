from utils.market_state import Market
from utils.create_new_items import TradingItem
from utils.create_new_items import max_item_price
from lifetime.predict_lifetime import predict_lifetime, correct_lifetime_prediction
import numpy
from math import isnan


def price_offer_decision(item: TradingItem, market: Market):
    if market.segmentation:
        segment = item.owner.segment
    else:
        segment = list(market.segments.keys())[0]  # major segment
    return item.price * (1 - market.segments[segment]['reduce_math_exp'])  # segment reduce math exp

def sell_items(market: Market, items_list: list, demand: int) -> (Market, int):
    items_pred = [item.lifetime_prob_real for item in items_list]
    weighted_pred = [el / sum(items_pred) for el in items_pred]
    while demand > 0 and len(items_list) > 0:
        sold_item_index = numpy.random.choice(range(len(items_list)), 1, p=weighted_pred)[0]
        sold_item = items_list[sold_item_index]
        if sold_item.possession == 'user':
            sold_item.income = sold_item.price * market.platform_interest
        elif sold_item.possession == 'platform':
            sold_item.income = sold_item.price
        sold_item.state = False
        demand -= 1
        del items_list[sold_item_index]
        del items_pred[sold_item_index]
        if len(items_list) > 0:
            weighted_pred = [el / sum(items_pred) for el in items_pred]
    return market, demand

def trading_algo(market: Market) -> Market:

    # STEP 1 - invest into new items
    if market.invest:
        new_items = [item for item in market.items if item.time_created_period == market.epoch]
        for brand in [brand for brand in market.all_models if brand in market.lifetime_models]:
            brand_ranking_list = sorted([item.lifetime_prob for item in market.items if item.state and
                                         (item.cur_time_period - item.time_created_period) <= 30 and
                                         item.cur_time_period == market.epoch and item.brand == brand and
                                         item.lifetime_prob >= 0.5], reverse=True)
            future_demand_expected = market.demand_30d_predictions_expected[brand][market.epoch]
            demand_threshold = int(future_demand_expected * market.decision_threshold)
            if demand_threshold > 0:
                for item in [item for item in new_items if item.brand == brand]:
                    if len(brand_ranking_list) > 0:
                        marginal_pred = brand_ranking_list[min([demand_threshold-1, len(brand_ranking_list) - 1])]
                    else:
                        marginal_pred = 0.5
                    if item.lifetime_prob > marginal_pred:
                        max_price = max_item_price(item, market, marginal_pred)
                        offered_price = price_offer_decision(item, market)
                        min_price = item.price * item.owner.max_reduce
                        if offered_price >= min_price and max_price - offered_price >= market.min_margin:
                            item.cost = offered_price * (1 - market.platform_interest)
                            item.price = max_price
                            item.possession = 'platform'
                            item.lifetime_prob = predict_lifetime(item, market)
                            item.lifetime_prob_real = correct_lifetime_prediction(market, item, item.lifetime_prob)

    # STEP 2 - check what is sold today
    for brand in market.all_models:
        cur_demand = market.demand_predictions_real[brand][market.epoch]
        if cur_demand > 0:
            best_items_list = [item for item in market.items if item.state and
                               (item.cur_time_period - item.time_created_period) <= 30 and
                               item.cur_time_period == market.epoch and item.brand == brand and
                               item.lifetime_prob_real >= 0.5]
            if len(best_items_list) > 0:
                market, cur_demand = sell_items(market, best_items_list, cur_demand)
        if cur_demand > 0:
            rest_items_list = [item for item in market.items if item.state and
                               item.cur_time_period == market.epoch and item.brand == brand]
            market, cur_demand = sell_items(market, rest_items_list, cur_demand)

    # STEP 3 - check who left the platform or next epoch for active
    for item in [item for item in market.items if item.state and item.cur_time_period == market.epoch]:
        if item.owner.days_abandoned <= item.cur_time_period - item.time_created_period and item.possession == 'user':
            item.state = False
        else:
            item.cur_time_period += 1

    return market

