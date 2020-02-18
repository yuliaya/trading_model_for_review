import pandas as pd
import os
import pickle

if __name__ == '__main__':
    brand_daily_supply = dict()
    for dataset in ['Chanel.pkl', 'LV.pkl', 'SL.pkl', 'Gucci.pkl', 'Fendi.pkl']:
        df = pd.read_pickle(dataset)
        min_date_df = pd.pivot_table(df, values='sc_date', index='id', aggfunc='min').reset_index()
        daily_items = pd.pivot_table(min_date_df, values='id', index='sc_date',
                                      aggfunc='count').reset_index()
        new_items_df = pd.DataFrame(set(df['sc_date']),columns=['sc_date']).sort_values('sc_date')
        stat_by_date = pd.merge(new_items_df, daily_items, how='left')[4:].fillna(0)
        brand_daily_supply[dataset[:-4]] = list(stat_by_date['id'])
    with open('brand_daily_supply.pkl', 'wb') as f:
        pickle.dump(brand_daily_supply, f)
