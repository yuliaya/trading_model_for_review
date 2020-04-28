import pickle
from utils.trading_item import TradingItem
from typing import List
import datetime
import numpy
import pandas as pd
from collections import defaultdict
import copy
from math import isnan


class Market:
    '''
    Defines current market state: Epoch, distribution of user features, distribution of product features etc
    '''
    def __init__(self,
                 lifetime_period: int = 1,
                 platform_interest: float = 0.2,
                 cur_date=datetime.date(2019, 1, 1),
                 invest: bool = True):
        self.invest = invest
        self.epoch = 0
        self.lifetime_period = lifetime_period  # number of epochs
        self.platform_interest = platform_interest  # commission for trading
        self.cur_date = cur_date
        with open('./decision_making/model_patameters.pkl', 'rb') as f:
            model_parameters = pickle.load(f)
        self.all_models = list(model_parameters.keys())
        self.model_general_parameters = model_parameters
        self.items: List[TradingItem] = []
        with open('./predict_demand/demand_models_spec.pkl', 'rb') as f:
            demand_models = pickle.load(f)
        self.demand_models = demand_models
        with open('./lifetime/lifetime_models_spec.pkl', 'rb') as f:
            lifetime_models = pickle.load(f)
        self.lifetime_models = lifetime_models
        with open('./data/median_prices.pkl', 'rb') as f:
            median_prices = pickle.load(f)
        self.median_prices = median_prices
        with open('./data/search_trends.pkl', 'rb') as f:
            search_trends = pickle.load(f)
        self.search_trends = search_trends
        with open('./data/retail_prices.pkl', 'rb') as f:
            retail_prices_dict = pickle.load(f)
        self.retail_prices_dict = retail_prices_dict
        self.encoders = {}
        for brand in self.all_models:
            if brand in self.lifetime_models.keys():
                self.encoders[brand] = {}
                df = self.lifetime_models[brand]['encoded_df']
                mean_label = numpy.mean(df['label'])
                self.encoders[brand]['color'] = dict(zip(df['bags_color'], df['bags_color_loo']))
                self.encoders[brand]['no_color'] = mean_label
                self.encoders[brand]['materials'] = dict(zip(df['materials_list'], df['materials_list_loo']))
                self.encoders[brand]['no_materials'] = mean_label
                if 'size_loo' in df.columns:
                    self.encoders[brand]['size'] = dict(zip(df['size'], df['size_loo']))
                    self.encoders[brand]['no_size'] = mean_label
        demand_predictions = {}
        demand_30d_predictions = {}
        for brand in self.all_models:
            demand_predictions[brand] = {}
            demand_30d_predictions[brand] = {}
        self.demand_predictions_real = copy.deepcopy(demand_predictions)
        self.demand_30d_predictions_real = copy.deepcopy(demand_30d_predictions)
        self.demand_predictions_expected = copy.deepcopy(demand_predictions)
        self.demand_30d_predictions_expected = copy.deepcopy(demand_30d_predictions)
        self.min_epoch = -45

    def stat_on_items(self):
        for brand in self.all_models:
            print('%s stats:' %brand)
            df = pd.DataFrame(0, columns=['New', 'Sold', 'Left'], index=range(self.min_epoch, self.epoch))
            for item in [i for i in self.items if i.brand == brand]:
                df.loc[item.time_created_period, 'New'] += 1
                if not item.state:
                    if item.income == 0:
                        df.loc[item.cur_time_period, 'Left'] += 1
                    else:
                        df.loc[item.cur_time_period, 'Sold'] += 1
            print(df.to_string())

    def update_median_prices(self):
        median_prices = {}
        for brand in self.all_models:
            median_prices[brand] = defaultdict(list)
        for item in [item for item in self.items if item.state and item.cur_time_period == self.epoch]:
                median_prices[item.brand][(item.size, item.material)].append(item.price)
                median_prices[item.brand][(item.size, item.material,
                                      item.condition)].append(item.price)
                median_prices[item.brand][(item.size, item.material,
                                      item.condition, item.color)].append(item.price)
                median_prices[item.brand][(item.size, item.condition)].append(item.price)
                median_prices[item.brand][item.material].append(item.price)
                median_prices[item.brand][item.size].append(item.price)
        for brand in list(median_prices.keys()):
            for l in list(median_prices[brand].keys()):
                median_prices[brand][l] = numpy.median(median_prices[brand][l])
        self.median_prices = copy.deepcopy(median_prices)


if __name__ == '__main__':
    m = Market()
    print(m.all_models)
    print(m.model_parameters)
