# -*- coding: utf-8 -*-
import operator
import pathlib
import numpy as np
import pandas as pd


def form_hhaa_records(df,
                       team_locn='h',
                       records='h',
                       feature = 'ftgoals'):
    """
    Accept a league table of matches with a feature
    """
    team_records = []
    for _, team_df in df.groupby(by=team_locn):
        lags = range(0, len(team_df))
        records_df = pd.DataFrame({f'{team_locn}_{records}_{feature}-{n}':
                                  team_df[team_locn + '_' + feature].shift(n) for n in lags})
        team_record = pd.concat([team_df, records_df], axis=1)
        team_records.append(team_record)
    full_df = pd.concat(team_records, axis=0).sort_index()
    return full_df

def col_hist_to_row_hist(df, team_locn, records, feat, team):
    feature = records + '_' + feat
    hist_df = df.copy(deep=True)[[team_locn, records, feature]]
    locn_inds = (hist_df[hist_df[team_locn] == team]).index
    hist_df.loc[locn_inds, feature] = np.NaN
    prevs = []
    for locn_ind in reversed(locn_inds):
        prev_values = hist_df.loc[:locn_ind, feature].dropna()
        prev = pd.DataFrame(np.flip(prev_values.values).reshape(1,-1), index = [locn_ind])
        prevs.append(prev)
    hist_df = pd.concat(prevs, axis=0, sort=True).sort_index()
    hist_df.columns = [team_locn + '_' + feature + '-' + str(n) for n in range(1,(hist_df.shape[1]+1), 1)]
    return hist_df

def form_ahha_records(df,
                       team_locn='h',
                       records='a',
                       feature = 'ftgoals'):
    """
    Accept a league table of matches with a feature
    """
    hist_dfs = []
    for team in df[team_locn].unique():
        crit1 = df[team_locn] == team ; crit2 = df[records] == team
        record_df = df[crit1 | crit2].drop(columns=[team_locn + '_' +feature, 'result'])
        hist_df = col_hist_to_row_hist(record_df, team_locn, records, feature, team)
        hist_dfs.append(hist_df)
    full_hist_df = pd.concat(hist_dfs, axis=0, sort=True).sort_index()
    full_df = pd.concat([df, full_hist_df], axis=1, sort=True).sort_index()
    return full_df


def form_feature_records(df, feature='ftgoals'):
    hh_records = form_hhaa_records(df, team_locn='h', records='h', feature='ftgoals')
    aa_records = form_hhaa_records(df, team_locn='a', records='a', feature='ftgoals')
    ah_records = form_ahha_records(df, team_locn='a', records='h', feature='ftgoals')
    ha_records = form_ahha_records(df, team_locn='h', records='a', feature='ftgoals')
    season_feature_df = pd.concat([hh_records, aa_records, ah_records, ha_records], axis=1)
    return season_feature_df


def transform_ts_to_supervised(league_seasons, features):
    all_dfs=[]
    for df in league_seasons:
        for feature in features:
            season_features = []
            season_feature_df = form_feature_records(df, feature)
            season_features.append(season_feature_df)
        season_all_features = pd.concat(season_features, axis=1)
        all_dfs.append(season_all_features)
    mega_df = pd.concat(all_dfs, axis=0)
    # Drop duplicate columns
    mega_df = mega_df.loc[:,~mega_df.columns.duplicated()]
    return mega_df

def get_league_seasons(top_level_dir):
    return ' '


test_df = pd.DataFrame({'date': ['25-may-2019', '25-may-2019', '1-june-2019',
                                     '1-june-2019', '8-june-2019', '8-june-2019',
                                     '15-june-2019', '15-june-2019', '22-june-2019',
                                     '29-june-2019', '29-june-2019', '6-july-2019'],
                            'h': ['A','C','B','D','A','B','C','D','D','A','B','C'],
                            'a': ['B','D','A','C','C','D','A','B','A','D','C','B'],
                            'h_ftgoals': [1,3,5,6,9,7,13,15,20,19,21,24],
                            'a_ftgoals': [0,4,2,6,8,10,12,16,20,18,22,24],
                            'result': ['hwin','awin','hwin','draw','hwin','awin',
                                       'hwin','awin','draw','hwin','awin','draw']})

print(test_df.head(15))
print('\n\n')

top_level_dir = ''
league_seasons = get_league_seasons(top_level_dir)
features = []
league_seasons = [test_df]
features = ['ftgoals']
mega_df = transform_ts_to_supervised(league_seasons, features)
print(mega_df.head(15))
# save_fp = ''
# mega_df.to_csv(save_fp, index=False)
