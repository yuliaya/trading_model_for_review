from utils.trading_item import TradingItem
from utils.market_state import Market
import pandas as pd
import numpy
import random
from statistics import stdev
from math import inf

def similar_stats(item: TradingItem, market: Market):
    keys = [(item.size, item.material, item.condition, item.color),
            (item.size, item.material, item.condition),
            (item.size, item.material),
            (item.size, item.condition),
            (item.material, item.condition),
            (item.material),
            (item.size)]

    for key in keys:
        if key in market.median_prices[item.brand]:
            if key == (item.size, item.material, item.condition, item.color):
                return len(market.median_prices[item.brand][key]),\
                       numpy.mean(market.median_prices[item.brand][key])
            else:
                return 0, numpy.mean(market.median_prices[item.brand][key])

    return 0, numpy.mean([i.price for i in market.items if
                          i.brand == item.brand and i.cur_time_period == market.epoch])

def retail_price(item: TradingItem, market: Market):
    if (item.color, item.material, item.size) in market.retail_prices_dict[item.brand]:
        return random.choice(market.retail_prices_dict[item.brand][(item.color, item.material, item.size)])
    elif (item.size, item.material) in market.retail_prices_dict[item.brand]:
        return random.choice(market.retail_prices_dict[item.brand][(item.size, item.material)])
    else:
        return random.choice(market.retail_prices_dict[item.brand][item.size])

def establish_median_price(item: TradingItem, market: Market):
    keys = [(item.size, item.material, item.condition, item.color),
            (item.size, item.material, item.condition),
            (item.size, item.material),
            (item.size, item.condition),
            (item.material, item.condition),
            item.material,
            item.size]

    for key in keys:
        if key in market.median_prices[item.brand].keys():
            key_list = market.median_prices[item.brand][key]
            if len(key_list) > 1:
                price = numpy.mean(key_list)
                std_dev = stdev(key_list)
                return_price = -inf
                while return_price < 0:
                    return_price = price + numpy.random.normal(0, std_dev)
                return return_price
            elif len(key_list) == 1:
                price = numpy.mean(key_list)
                if len([i.price for i in market.items if i.brand == item.brand and
                                 i.cur_time_period == market.epoch]) > 1:
                    std_dev = stdev([i.price for i in market.items if i.brand == item.brand and
                                     i.cur_time_period == market.epoch])
                elif len([i.price for i in market.items if i.brand == item.brand]) > 1:
                    std_dev = stdev([i.price for i in market.items if i.brand == item.brand])
                if std_dev:
                    return_price = -inf
                    while return_price < 0:
                        return_price = price + numpy.random.normal(0, std_dev)
                    return return_price

    return numpy.median([i.price for i in market.items if i.brand == item.brand and
                      i.cur_time_period > market.epoch - 5])


def correct_lifetime_prediction(market: Market, item: TradingItem, pred: float):
    if market.lifetime_models is None:
        return 0
    elif round(pred, 0) == 1 and item.brand in market.lifetime_models:
        if market.lifetime_accuracy is None:
            class1_precision = market.lifetime_models[item.brand]['precision_class1']
        else:
            class1_precision = market.lifetime_accuracy
        return numpy.random.choice([numpy.random.uniform (0, 0.5, 1)[0], pred],
                                    p=(1 - class1_precision, class1_precision))
    elif round(pred, 0) == 0 and item.brand in market.lifetime_models:
        if market.lifetime_accuracy is None:
            class0_precision = market.lifetime_models[item.brand]['precision_class0']
        else:
            class0_precision = market.lifetime_accuracy
        return numpy.random.choice ([pred, numpy.random.uniform (0.5, 1, 1)[0]],
                                    p=(class0_precision, 1 - class0_precision))
    else:
        return 0.5

def predict_lifetime(item: TradingItem, market:Market):
    if market.lifetime_models is None or item.brand not in market.lifetime_models.keys():
        return 0.5
    else:
        features = list(market.lifetime_models[item.brand]['features'])
        feature_dict = {}
        for feature in [f for f in features if f.startswith('search_')]:
            feature_dict[feature] = market.search_trends[item.brand][feature][market.cur_date]
        if 'number_similar' in features:
            feature_dict['number_similar'] = similar_stats(item, market)[0]
        if 'bags_price_refined' in features:
            feature_dict['bags_price_refined'] = item.price
        for feature in [f for f in features if f.startswith('bags_condition_')]:
            condition = feature.split("_")[2]
            feature_dict[feature] = (item.size == condition)
        if 'retail_price_refined' in features:
            feature_dict['retail_price_refined'] = item.retail_price
        if 'bags_color_loo' in features:
            if item.color in market.encoders[item.brand]['color'].keys():
                feature_dict['bags_color_loo'] = market.encoders[item.brand]['color'][item.color]
            else:
                feature_dict['bags_color_loo'] = market.encoders[item.brand]['no_color']
        if 'materials_list_loo' in features:
            if item.material in market.encoders[item.brand]['materials'].keys():
                feature_dict['materials_list_loo'] = market.encoders[item.brand]['materials'][item.material]
            else:
                feature_dict['materials_list_loo'] = market.encoders[item.brand]['no_materials']
        if 'size_loo' in features:
            if item.size in market.encoders[item.brand]['size'].keys():
                feature_dict['size_loo'] = market.encoders[item.brand]['size'][item.size]
            else:
                feature_dict['size_loo'] = market.encoders[item.brand]['no_size']
        if 'original_to_avg' in features:
            try:
                feature_dict['original_to_avg'] = item.price / similar_stats(item, market)[1]
            except:
                pass
        if 'price_to_retail' in features:
            feature_dict['price_to_retail'] = item.price / item.retail_price
        if 'const' in features:
            feature_dict['const'] = 1
        # print(feature_dict)
        train_df = pd.DataFrame({feature: [feature_dict[feature]] for feature in features})
        pred_df = market.lifetime_models[item.brand]['model'].predict_proba(train_df)

        pred = list(pred_df)[0][1]
        return pred

