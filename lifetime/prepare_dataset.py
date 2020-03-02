import pandas as pd
import datetime
from collections import defaultdict
import numpy as np
from math import isnan
import os
import re

if __name__ == '__main__':

    data_dir = './data/'
    brand = 'Chanel'
    df = pd.read_pickle(data_dir+'%s.pkl' % brand)
    print(df.shape)

    for file in [f for f in os.listdir(data_dir) if re.search('%s_search'%brand, f)]:
        search_df = pd.read_csv(data_dir+'%s' %file)
        search_df = search_df.reset_index()[1:]
        search_df['index'] = pd.to_datetime(search_df['index'])
        search_dict = dict(zip(search_df['index'],
            [int(item) for item in search_df['Category: All categories']]))
        keyword = 'search_' + file.split('_search_')[1][:-4]
        df[keyword] = df['sc_date'].map(search_dict)

    # stats on similar items
    item_stats = defaultdict(list)
    for i, row in df[-df['bags_price_refined'].isnull()].iterrows():
        key = (row['sc_date'], row['bags_color'], row['bags_condition'], row['materials_list'])
        item_stats[key].append(row['bags_price_refined'])

    min_dates = pd.pivot_table(df, values='sc_date', index='id', aggfunc='min').reset_index()
    max_dates = pd.pivot_table(df[-df['bags_price_refined'].isnull()], values='sc_date', index='id',
                               aggfunc='max').reset_index()

    df = pd.merge(df, max_dates, how='left', on='id',suffixes=('', '_last_date'))
    df = pd.merge(df, min_dates, how='left', on='id',suffixes=('', '_first_date'))

    first_date = min(df['sc_date'])
    last_date = max(df['sc_date'])

    # df = df[df.apply(lambda x: x['sc_date'] == x['sc_date_first_date'], axis = 1)]
    df = df[-df['sc_date_last_date'].isnull()]

    def days_live(row):
        if row['sc_date_first_date'] > first_date+datetime.timedelta(days=3):
            if row['sc_date_last_date'] == last_date:
                return [(row['sc_date_last_date']-row['sc_date']).days, 'Pending']
            else:
                return [(row['sc_date_last_date'] - row['sc_date']).days, 'Complete']
         else:
             return [None, None]

    df['lifetime'], df['status'] = zip(*df.apply(lambda x: days_live(x), axis = 1))

    df = df[-df['lifetime'].isnull()]

    daily_likes = defaultdict(dict)

    for i, row in df.iterrows():
        daily_likes[row['id']][row['sc_date']] = row['likes']

    def avg_daily_likes(id, date, ndays):
        d = daily_likes[id]
        dates = [day for day in d.keys() if day <= date and \
         date - datetime.timedelta(days=ndays) <= day]
        if len(dates) > 1:
            return (d[date] - d[min(dates)]) / (date - min(dates)).days
        else:
            return d[date]

    df['likes_last_1'] = df.apply(lambda x: avg_daily_likes(x['id'], x['sc_date'], 1), axis = 1)
    df['likes_last_7'] = df.apply(lambda x: avg_daily_likes(x['id'], x['sc_date'], 7), axis = 1)

    def similar_stats(date, color, condition, material):
        features = (date, color, condition, material)
        return pd.Series((len(item_stats[features]), np.mean(item_stats[features])))

    df[['number_similar', 'avg_similar']] = df.apply(lambda x:
        similar_stats(x['sc_date'], x['bags_color'], x['bags_condition'],
                      x['materials_list']), axis=1)

    df['bags_price_refined'] = df.apply(lambda x: x['bags_price_refined'] if not isnan(x['bags_price_refined']) \
                                        else x['sold_price_refined'], axis = 1)
    df['original_to_avg'] = df.apply(lambda x: x['bags_price_refined'] / x['avg_similar'], axis = 1)
    df['retail_price_refined'] = df['retail_price_refined'].fillna(df['retail_price_refined'].mean())

    print(df['retail_price_refined'].isnull().sum())
    # todo missing values for the field "retail_price_refined"

    df.to_pickle(data_dir+'%s_refined_new.pkl' %brand)

