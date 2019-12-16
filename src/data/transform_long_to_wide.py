# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
import pathlib

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    make_equiv_image_dest_fps)

PROJECT_DIR = pathlib.Path().cwd().resolve()


FEATURED_DIR = PROJECT_DIR / 'data' / '07-time-series-featured'
TRANSFORMED_DIR = PROJECT_DIR / 'data' / '08-transformed'


def form_hhaa_records(df,
                      team_locn='h',
                      records='h',
                      feature='ftGoals'):
    """
    Accept a league table of matches with a feature
    """
    team_records = []
    for _, team_df in df.groupby(by=team_locn):
        lags = range(0, len(team_df))
        records_df = pd.DataFrame({f'{team_locn}_{records}_{feature}-{n}':
                                  team_df[team_locn + '_' + feature].shift(n)
                                  for n in lags})
        team_record = pd.concat([team_df, records_df], sort=True, axis=1)
        team_records.append(team_record)
    full_df = pd.concat(team_records, axis=0, sort=True).sort_index()
    return full_df


def col_hist_to_row_hist(df, team_locn, records, feat, team):
    feature = records + '_' + feat
    hist_df = df.copy(deep=True)[[team_locn, records, feature]]
    locn_inds = (hist_df[hist_df[team_locn] == team]).index
    hist_df.loc[locn_inds, feature] = np.NaN
    prevs = []
    for locn_ind in reversed(locn_inds):
        prev_values = hist_df.loc[:locn_ind, feature].dropna()
        prev = pd.DataFrame(np.flip(prev_values.values).reshape(1, -1),
                            index=[locn_ind])
        prevs.append(prev)
    hist_df = pd.concat(prevs, axis=0, sort=True).sort_index()
    hist_df.columns = [team_locn + '_' + feature + '-' + str(n) for
                       n in range(1, (hist_df.shape[1]+1), 1)]
    return hist_df


def form_ahha_records(df,
                      team_locn='h',
                      records='a',
                      feature='ftGoals'):
    """
    Accept a league table of matches with a feature
    """
    hist_dfs = []
    for team in df[team_locn].unique():
        crit1 = df[team_locn] == team
        crit2 = df[records] == team
        record_df = df[crit1 | crit2].drop(columns=[team_locn +
                                                    '_' + feature, 'result'])
        hist_df = col_hist_to_row_hist(record_df,
                                       team_locn,
                                       records,
                                       feature,
                                       team)
        hist_dfs.append(hist_df)
    full_hist_df = pd.concat(hist_dfs, axis=0, sort=True).sort_index()
    full_df = pd.concat([df, full_hist_df], axis=1, sort=True).sort_index()
    return full_df


def form_feature_records(df, feature='ftGoals'):
    hh_records = form_hhaa_records(df, team_locn='h', records='h',
                                   feature=feature)
    aa_records = form_hhaa_records(df, team_locn='a', records='a',
                                   feature=feature)
    ah_records = form_ahha_records(df, team_locn='a', records='h',
                                   feature=feature)
    ha_records = form_ahha_records(df, team_locn='h', records='a',
                                   feature=feature)
    season_feature_df = pd.concat([hh_records, aa_records, ah_records,
                                   ha_records], sort=True, axis=1)
    return season_feature_df


def transform_ts_to_supervised(df, features):
    features = np.unique([col[2:] for col in df.columns
                          if col.startswith('h_')])
    all_dfs = []
    # for df in league_seasons:
    season_features = []
    for feature in features:
        # season_features = []
        season_feature_df = form_feature_records(df, feature)
        season_features.append(season_feature_df)
    season_all_features = pd.concat(season_features, sort=True, axis=1)
    all_dfs.append(season_all_features)
    mega_df = pd.concat(all_dfs, axis=0)
    # Drop duplicate columns
    mega_df = mega_df.loc[:, ~mega_df.columns.duplicated()]
    return mega_df


test_df = pd.DataFrame({'date': ['25-may-2019', '25-may-2019', '1-june-2019',
                                 '1-june-2019', '8-june-2019', '8-june-2019',
                                 '15-june-2019', '15-june-2019',
                                 '22-june-2019', '29-june-2019',
                                 '29-june-2019', '6-july-2019'],
                        'h': ['A', 'C', 'B', 'D', 'A', 'B', 'C', 'D', 'D',
                              'A', 'B', 'C'],
                        'a': ['B', 'D', 'A', 'C', 'C', 'D', 'A', 'B', 'A',
                              'D', 'C', 'B'],
                        'h_ftGoals': [1, 3, 5, 6, 9, 7, 13, 15, 20, 19, 21,
                                      24],
                        'a_ftGoals': [0, 4, 2, 6, 8, 10, 12, 16, 20, 18, 22,
                                      24],
                        'result': ['hwin', 'awin', 'hwin', 'draw', 'hwin',
                                   'awin', 'hwin', 'awin', 'draw', 'hwin',
                                   'awin', 'draw']})


def run_transform_ts_to_supervised():
    filepaths = get_filepaths(FEATURED_DIR, ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    features = None
    df_tss = []
    for df in dfs:
        # Need to group by season here before applying transform
        # Then need to restack after transformation applied
        season_dfs = []
        for ind, season_df in df.groupby(by='season'):
            season_df_t = transform_ts_to_supervised(season_df, features)
            season_dfs.append(season_df_t)
        league_df = pd.concat(season_dfs, sort=True, axis=0)
        df_tss.append(league_df)
    transformed_filepaths = make_equiv_image_dest_fps(FEATURED_DIR,
                                                      TRANSFORMED_DIR,
                                                      filepaths)
    n_saved = write_dfs_to_filepaths(df_tss, transformed_filepaths)
    print(n_saved)


if __name__ == "__main__":
    run_transform_ts_to_supervised()
