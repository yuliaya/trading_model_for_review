from utils.market_state import Market
from utils.trading_item import TradingItem
from utils.trading_item import User
import numpy
import os
import pandas as pd
import re
from datetime import timedelta, date
from lifetime.predict_lifetime import predict_lifetime, establish_median_price, retail_price, correct_lifetime_prediction
import copy


def establish_price(item: TradingItem, market: Market):
    price = establish_median_price(item, market)
    return price

def initiate_items_list(market):
    dir = './data/'
    min_df_date = date(2019,1,1)
    for brand_file in [f for f in os.listdir(dir) if f.endswith('refined.pkl')]:
        df = pd.read_pickle(dir+brand_file)
        first_df_date = min(df['sc_date'])
        if first_df_date > min_df_date:
            min_df_date = first_df_date

    min_df_date = min_df_date + timedelta(days=1)
    market.cur_date = min_df_date + timedelta(days=45)

    for brand_file in [f for f in os.listdir(dir) if f.endswith('refined.pkl')]:
        df = pd.read_pickle(dir+brand_file)
        brand = brand_file.split('_')[0]
        if market.lifetime_models is not None and brand in market.lifetime_models.keys():
            prob_df = market.lifetime_models[brand]['test_reults_df']
            best_model = re.search("(.*)_pred", market.lifetime_models[brand]['name']).group(1)
            item_probs = dict(zip(prob_df['id'], prob_df['%s_prob' % best_model]))
        else:
            item_probs = None

        cur_df = df[df['sc_date'].map(lambda x: min_df_date <= x < min_df_date + timedelta(days=45))]
        cur_df = cur_df[cur_df['sc_date_first_date'].map(lambda x: min_df_date <= x)]

        existing_items = set()
        for i, row in cur_df.iterrows():
            cur_time_period = None
            if row['id'] not in existing_items:
                if row['sc_date_first_date'] <= min_df_date:
                    time_created_period = -45
                else:
                    time_created_period = (row['sc_date_first_date'] - min_df_date).days - 45
                if row['sc_date_last_date'] < min_df_date + timedelta(days=45):
                    cur_time_period = (row['sc_date_last_date'] - (min_df_date + timedelta(days=45))).days
                new_item = TradingItem(market=market,
                                       time_created_period=time_created_period,
                                       brand=row['bags_brand'],
                                       color=row['bags_color'],
                                       size=row['size'],
                                       material=row['materials_list'],
                                       condition=row['bags_condition'])
                new_item.price = row['bags_price_refined']
                new_item.retail_price = row['retail_price_refined']
                if cur_time_period:
                    new_item.cur_time_period = cur_time_period
                    new_item.state = False
                    if row['ever_sold'] == 1:
                        new_item.income = new_item.price * market.platform_interest
                    else:
                        new_item.owner.days_abandoned = cur_time_period - time_created_period
                else:
                    scale = market.model_general_parameters[brand]['days_abandoned_exp_scale']
                    new_item.owner.days_abandoned = round(numpy.random.exponential(scale), 0)
                    leave_expected_period = new_item.time_created_period + new_item.owner.days_abandoned
                    if leave_expected_period < 0:
                        new_item.cur_time_period = leave_expected_period
                        new_item.state = False
                    else:
                        new_item.cur_time_period = 0
                if item_probs:
                    new_item.lifetime_prob = item_probs.get(row['id'])
                    if not new_item.lifetime_prob:
                        new_item.lifetime_prob = predict_lifetime(new_item, market)
                    new_item.lifetime_prob_real = correct_lifetime_prediction(
                            market, new_item, new_item.lifetime_prob)
                else:
                    new_item.lifetime_prob = 0.5
                    new_item.lifetime_prob_real = 0.5
                market.items.append(new_item)
                existing_items.add(row['id'])

    return market

def create_items(market: Market):

    new_items_list = list()
    for model in market.all_models:
        model_params = market.model_general_parameters[model]
        model_new_amount = int(round(numpy.random.exponential(model_params['daily_new_amount']), 0))
        for i in range(model_new_amount):
            bags_size = numpy.random.choice(list(model_params['sizes'].keys()),
                                             p=list(model_params['sizes'].values()))
            bags_condition = numpy.random.choice(list(model_params['conditions'].keys()),
                                              p=list(model_params['conditions'].values()))
            bags_material = numpy.random.choice(list(model_params['materials'].keys()),
                                              p=list(model_params['materials'].values()))
            bags_color = numpy.random.choice(list (model_params['colors'].keys()),
                                              p=list(model_params['colors'].values()))
            # print(bags_size, bags_condition, bags_material, bags_color)
            new_item = TradingItem(market=market,
                                   time_created_period=market.epoch,
                                   brand=model,
                                   color=bags_color,
                                   size=bags_size,
                                   material=bags_material,
                                   condition=bags_condition)
            new_item.price = establish_price(new_item, market)
            new_item.retail_price = retail_price(new_item, market)
            ab_scale = market.model_general_parameters[model]['days_abandoned_exp_scale']
            new_item.owner.days_abandoned = round(numpy.random.exponential(ab_scale), 0)
            new_item.lifetime_prob = predict_lifetime(new_item, market)
            new_item.lifetime_prob_real = correct_lifetime_prediction(market, new_item, new_item.lifetime_prob)
            new_items_list.append(new_item)
    market.items.extend(new_items_list)

    return market


def max_item_price(item: TradingItem, market: Market, marginal_pred: float):
    new_item = copy.deepcopy(item)
    while predict_lifetime(new_item,market) >= marginal_pred and\
            (new_item.price - item.price) <= market.max_margin:
        new_item.price += 100
    return new_item.price - 100