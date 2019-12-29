import pathlib
import sys

from itertools import chain

import pandas as pd

from category_encoders import OrdinalEncoder
from category_encoders import OneHotEncoder

PROJECT_DIR = pathlib.Path().cwd().resolve()
sys.path.append(str(PROJECT_DIR))

from src.data.pfuncs import (get_filepaths,
                             read_csvs_to_dfs,
                             write_dfs_to_filepaths,
                             make_equiv_image_dest_fps) # noqa E402

from src.models.poisson_regression import PoissonRegression # noqa E402
from src.models.splitter import LeagueSeasonTimeSeriesFold # noqa E402

STACKED_DIR = PROJECT_DIR / 'data' / '06-stacked-seasons'
FEATURED_DIR = PROJECT_DIR / 'data' / '07-time-series-featured'


def clean_df(df_orig):
    """
    Note - This does not return ALL columns!
    """
    df = df_orig.copy(deep=True)
    first_cols = ['nation', 'league', 'season', 'h', 'a', 'date',
                  'h_ftGoals', 'a_ftGoals', 'result',
                  'seasonPercentile', 'implied_hwin',
                  'implied_draw', 'implied_awin']
    h_feature_cols = sorted([col for col in df.columns if col[0:2] == 'h_'])
    a_feature_cols = sorted([col for col in df.columns if col[0:2] == 'a_'])
    full_odds_cols = sorted([col for col in df.columns if 'Odds' in col
                            and len(df[col].dropna()) == len(df)])

    df.sort_values(by=['season', 'date'], ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df_h = df[h_feature_cols].apply(pd.to_numeric,
                                    errors='coerce',
                                    downcast='float')
    df_a = df[a_feature_cols].apply(pd.to_numeric,
                                    errors='coerce',
                                    downcast='float')

    df_readable = pd.concat([df[first_cols], df_h, df_a, df[full_odds_cols]],
                            sort=False, axis=1)
    dropper_cols = [col for col in df_readable.columns if '2.5Odds' in col or
                    'asian' in col]
    df_readable.drop(columns=dropper_cols, inplace=True)
    list1 = ['hwinOddsBet365', 'drawOddsBet365', 'awinOddsBet365']
    if set(list1) <= set(df_readable.columns):
        mapping_dict = {col: col[0:8] for col in list1}
        df_readable.rename(columns=mapping_dict, inplace=True)

    if 'h_htgoals' in df_readable.columns:
        df_readable.drop(columns=['h_htgoals'], inplace=True)
    if 'a_htgoals' in df_readable.columns:
        df_readable.drop(columns=['a_htgoals'], inplace=True)

    return df_readable


def drop_artefact_cols(df_orig):
    df = df_orig.copy(deep=True)
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def insert_game_day(df_orig):
    df = df_orig.copy(deep=True)
    df['game_day'] = df.groupby(by='date').ngroup(ascending=True)
    return df


def insert_seasonPercentile(df_orig):
    df = df_orig.copy(deep=True)
    df['seasonPercentile'] = df['game_day'].rank(method='max', pct=True)
    return df


def encode_result(df_orig):
    df = df_orig.copy(deep=True)
    mapping_dict = {'col': 'result', 'mapping': {'hwin': 1,
                                                 'draw': 2,
                                                 'awin': 3}}
    ord_enc = OrdinalEncoder(mapping=[mapping_dict])
    df['ordinal_result'] = ord_enc.fit_transform(df[['result']])
    return df


def one_hot_encoded_result(df_orig):
    df = df_orig.copy(deep=True)
    one_hot_enc = OneHotEncoder(cols=['ordinal_result'], use_cat_names=True)
    one_hot_cols = one_hot_enc.fit_transform(df[['ordinal_result']])
    new_one_hot_col_names = [col[:-2] for col in one_hot_cols.columns]
    mapping_dict = {old: new for old, new in zip(one_hot_cols.columns,
                                                 new_one_hot_col_names)}
    one_hot_cols.rename(columns=mapping_dict, inplace=True)
    one_hot_cols = one_hot_cols[sorted(one_hot_cols.columns)]
    df_with_new_cols = pd.concat([df, one_hot_cols], axis=1)
    return df_with_new_cols


def run_poisson_regression(df_orig):
    df = df_orig.copy(deep=True)
    df.reset_index(drop=True, inplace=True)
    game_day_splitter = LeagueSeasonTimeSeriesFold()
    for train_indices, predict_indices in game_day_splitter.split(df):
        clf = PoissonRegression()
        clf.fit(df.loc[train_indices], df.loc[train_indices, 'result'])
        preds = clf.predict_proba(df.loc[predict_indices])
        for i, col in enumerate(preds.columns):
            df.loc[preds.index, preds.columns[i]] = \
                preds[preds.columns[i]].values
    return df


def insert_implied_probabilities(df_orig):
    df = df_orig.copy(deep=True)
    """
    Accepts a DataFrame containing 3 specified ordered columns
    The columns are odds and must be in the order
    home win, draw, away win
    """
    df = df_orig.copy(deep=True)
    odds_cols = ['hwinOdds', 'drawOdds', 'awinOdds']
    if odds_cols[0] in df.columns:
        tot = 1/df[odds_cols[0]] + 1/df[odds_cols[1]] + 1/df[odds_cols[2]]
        hwin = 1/df[odds_cols[0]]/tot
        draw = 1/df[odds_cols[1]]/tot
        awin = 1/df[odds_cols[2]]/tot
        df['implied_hwin'] = hwin
        df['implied_draw'] = draw
        df['implied_awin'] = awin
    return df


def apply_features(dfs):
    featured_dfs = []
    for df in dfs:
        # print(df.columns)
        season_dfs = []
        seasons = sorted(df['season'].unique())
        for season in seasons:
            season_df = df[df['season'] == season]
            season_df.reset_index(drop=True, inplace=True)
            # print(season_df['season'].unique())
            # print(sorted(df['h'].unique()))
            # print(sorted(df['a'].unique()))
            season_df = insert_game_day(season_df)
            season_df = insert_seasonPercentile(season_df)
            season_df = insert_implied_probabilities(season_df)
            season_df = encode_result(season_df)
            season_df = one_hot_encoded_result(season_df)
            season_df = run_poisson_regression(season_df)
            season_dfs.append(season_df)
            # break
        # common_cols = list(set.intersection(*(set(df.columns)
        #                    for df in season_dfs)))
        # featured_df = pd.concat([df[common_cols] for df in season_dfs], axis=0)
        list_of_dicts = [cur_df.T.to_dict().values() for cur_df in season_dfs]
        featured_df = pd.DataFrame(list(chain(*list_of_dicts)))
        featured_df = clean_df(featured_df)
        featured_df = drop_artefact_cols(featured_df)
        featured_dfs.append(featured_df)
    return featured_dfs


def apply_ts_features():
    filepaths = get_filepaths(STACKED_DIR, ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    featured_dfs = apply_features(dfs)
    featured_filepaths = make_equiv_image_dest_fps(STACKED_DIR,
                                                   FEATURED_DIR,
                                                   filepaths)
    n_saved = write_dfs_to_filepaths(featured_dfs, featured_filepaths)
    print(n_saved)


if __name__ == "__main__":
    apply_ts_features()
