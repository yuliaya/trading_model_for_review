import pandas as pd
import datetime
from collections import defaultdict
import numpy as np
from scipy import stats
import pickle


def add_retail_price(row):
    if row['retail_price_refined'] is None:
        key = (row['bags_color'], row['materials_list'], row['size'])
        if key in model_stats:
            return np.mean(model_stats[key])
        else:
            return np.mean(model_stats[row['size']])
    else:
        return row['retail_price_refined']

def days_live(row):
    if row['sc_date_first_date'] > first_date+datetime.timedelta(days=1):
        if row['sc_date_last_date'] == last_date:
            return [(row['sc_date_last_date']-row['sc_date']).days, 'Pending']
        else:
            return [(row['sc_date_last_date'] - row['sc_date']).days, 'Complete']
    else:
        return [None, None]

def similar_stats(date, color, condition, material, size):
    features = (date, color, condition, material, size)
    if features in item_stats:
        return pd.Series((len(item_stats[features]), np.mean(item_stats[features])))
    else:
        return pd.Series((0, np.mean(item_stats[(date, size, condition)])))


def custom_percentile(date, color, condition, material, size, price):
    features = (date, color, condition, material, size)
    list_of_values = item_stats[features]
    return stats.percentileofscore (list_of_values, price)


if __name__ == '__main__':

    data_dir = '../data/'
    brand = 'Gucci'
    df = pd.read_pickle(data_dir+'%s.pkl' % brand)
    print(df.shape)
    print(min(df['sc_date']))
    print(max(df['sc_date']))

    with open(data_dir+'search_trends.pkl', 'rb') as f:
        trends_dict = pickle.load(f)

    for keyword in list(trends_dict[brand].keys()):
        df[keyword] = df['sc_date'].map(trends_dict[brand][keyword])

    # retail pricing stats for color+material

    model_stats = defaultdict(list)
    for i, row in df[['id', 'bags_color', 'materials_list', 'retail_price_refined', 'size']].\
            drop_duplicates().iterrows():
        if row['retail_price_refined'] is not None:
            key = (row['bags_color'], row['materials_list'], row['size'])
            model_stats[key].append(row['retail_price_refined'])
            model_stats[(row['size'], row['materials_list'])].append(row['retail_price_refined'])
            model_stats[row['size']].append(row['retail_price_refined'])

    with open(data_dir+'retail_prices.pkl', 'rb') as f:
        retail_prices_dict = pickle.load(f)

    retail_prices_dict[brand] = model_stats

    with open(data_dir+'retail_prices.pkl', 'wb') as f:
        pickle.dump(retail_prices_dict, f)

    # add retail price if missing
    df['retail_price_refined'] = df.apply(lambda x: add_retail_price(x), axis = 1)

    min_dates = pd.pivot_table(df, values='sc_date', index='id', aggfunc='min').reset_index()
    max_dates = pd.pivot_table(df[-df['bags_price_refined'].isnull()], values='sc_date', index='id',
                               aggfunc='max').reset_index()

    df = pd.merge(df, max_dates, how='left', on='id',suffixes=('', '_last_date'))
    df = pd.merge(df, min_dates, how='left', on='id',suffixes=('', '_first_date'))

    first_date = min(df['sc_date'])
    last_date = max(df['sc_date'])

    # df = df[df.apply(lambda x: x['sc_date'] == x['sc_date_first_date'], axis = 1)]

    # remove items that were sold before we started tracking
    df = df[-df['sc_date_last_date'].isnull()]

    # check if ever sold
    never_sold_items = set(df['id']) - \
                       set(df[-df['sold_price_refined'].isnull()]['id'])

    df['ever_sold'] = df['id'].map(lambda x: 0 if x in never_sold_items else 1)

    df['lifetime'], df['status'] = zip(*df.apply(lambda x: days_live(x), axis = 1))

    # df = df[-df['lifetime'].isnull()]

    # daily_likes = defaultdict(dict)
    #
    # for i, row in df.iterrows():
    #     daily_likes[row['id']][row['sc_date']] = row['likes']
    #
    # def avg_daily_likes(id, date, ndays):
    #     d = daily_likes[id]
    #     dates = [day for day in d.keys() if day <= date and \
    #      date - datetime.timedelta(days=ndays) <= day]
    #     if len(dates) > 1:
    #         return (d[date] - d[min(dates)]) / (date - min(dates)).days
    #     else:
    #         return d[date]
    #
    # df['likes_last_1'] = df.apply(lambda x: avg_daily_likes(x['id'], x['sc_date'], 1), axis = 1)
    # df['likes_last_7'] = df.apply(lambda x: avg_daily_likes(x['id'], x['sc_date'], 7), axis = 1)
    # pricing stats on similar items for each day

    # if item was sold but put back on the next day
    df['bags_price_refined'] = df.apply(lambda x: x['bags_price_refined'] if x['bags_price_refined'] is not None \
                                        else x['sold_price_refined'], axis = 1)
    df = df[-df['bags_price_refined'].isnull()]

    item_stats = defaultdict(list)
    for i, row in df[-df['bags_price_refined'].isnull()].iterrows():
        key = (row['sc_date'], row['bags_color'], row['bags_condition'], row['materials_list'], row['size'])
        item_stats[key].append(row['bags_price_refined'])
        item_stats[(row['sc_date'], row['size'], row['bags_condition'])].append(row['bags_price_refined'])

    df[['number_similar', 'avg_similar']] = df.apply(lambda x:
        similar_stats(x['sc_date'], x['bags_color'], x['bags_condition'],
                      x['materials_list'], x['size']), axis=1)

    df['original_to_avg'] = df.apply(lambda x: x['bags_price_refined'] / x['avg_similar'], axis = 1)
    df['price_to_retail'] = df.apply(lambda x: x['bags_price_refined'] / x['retail_price_refined'], axis = 1)

    df['price_percentile'] = df.apply(lambda x:
                                      custom_percentile(x['sc_date'], x['bags_color'], x['bags_condition'],
                                                    x['materials_list'], x['size'], x['bags_price_refined']), axis=1)

    print(df.isnull().sum())
    df.to_pickle(data_dir+'%s_refined.pkl' %brand)
