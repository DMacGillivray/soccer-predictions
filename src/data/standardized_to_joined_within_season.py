import pathlib
import sys

import pandas as pd

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    make_filepaths_from_dfs,
                    get_matching_filepaths)

PROJECT_DIR = pathlib.Path().cwd().resolve()
STDZED_DIR = PROJECT_DIR / 'data' / '04-standardized'
JOINED_DIR = PROJECT_DIR / 'data' / '05-joined'


def merger(football_df, odds_df2):
    # dfs = sorted(list(df_dict.values()), key=lambda x: len(x), reverse=True)
    # merge_asof on date using home team, awat_team, home_goals,
    # and away_goals to match
    # merge_asof does a left join, so put longest daf on left, so get max
    # data into merged
    merged = pd.merge_asof(football_df, odds_df2,
                           on='date',
                           by=['h', 'a', 'h_ftGoals', 'a_ftGoals'],
                           suffixes=('_ic', '_fdcu'),
                           tolerance=pd.Timedelta(days=2),
                           direction='nearest'
                           )
    # # Put a date difference column into the merged df
    # merged['dates_diff'] = merged['date_ic'] - merged['date_fdcu']
    # # Write the merge issues data to a yaml file

    merged.sort_values(by='date', ascending=True, inplace=True)
    return merged


def do_merge(left_dfs, right_dfs):
    merged_dfs = []
    for left_df, right_df in zip(left_dfs, right_dfs):
        # print(left_df['nation'].unique(),
        #         left_df['league'].unique(),
        #         left_df['season'].unique())
        # print(right_df['nation'].unique(),
        #         right_df['league'].unique(),
        #         right_df['season'].unique())

        # cast to float to enable a join cannot join on integer and float
        # This should move into Clean
        left_df['date'] = pd.to_datetime(left_df['date'])
        right_df['date'] = pd.to_datetime(right_df['date'])

        cols = ['h_ftGoals', 'a_ftGoals']
        left_df[cols] = left_df[cols].apply(pd.to_numeric,
                                            errors='coerce',
                                            downcast='float',
                                            axis=1)
        right_df[cols] = right_df[cols].apply(pd.to_numeric,
                                              errors='coerce',
                                              downcast='float',
                                              axis=1)

        left_df.sort_values(by=['date', 'h', 'a'], inplace=True)
        right_df.sort_values(by=['date', 'h', 'a'], inplace=True)

        # if 'et_pen_awd' in right_df.columns:
        #     #if right_df['et_pen_awd'].null().sum() > 0:
        #     inds = right_df.index[~right_df['et_pen_awd'].isnull()].tolist()
        #     for ind in inds:
        #         print(f'ind: {ind}')
        #         # right_df['h_ftGoals'] = np.NaN
        #         # right_df['a_ftGoals'] = np.NaN

        try:
            merged_df = pd.merge_asof(left_df, right_df,
                                      on='date',
                                      by=['h', 'a', 'h_ftGoals', 'a_ftGoals',
                                          'nation', 'league', 'season',
                                          'result'],
                                      suffixes=('_ic', '_fdcu'),
                                      tolerance=pd.Timedelta(days=10),
                                      direction='nearest')
            merged_df.sort_values(by='date', ascending=True, inplace=True)
            merged_dfs.append(merged_df)
        except pd.errors.MergeError:
            # raise pd.errors.MergeError
            err = sys.exc_info()[0]
            print("MergeError:", err, err.args)
            return left_df

    return merged_dfs


def join_within_league_seasons(sources):
    left_df_fps = get_filepaths(STDZED_DIR / sources[0], ext='csv')
    right_df_fps = get_filepaths(STDZED_DIR / sources[1], ext='csv')
    left_df_fps, right_df_fps = get_matching_filepaths(left_df_fps,
                                                       right_df_fps,
                                                       sources[0],
                                                       sources[1])
    left_dfs = read_csvs_to_dfs(left_df_fps)
    right_dfs = read_csvs_to_dfs(right_df_fps)
    merged_dfs = do_merge(left_dfs, right_dfs)

    merged_fps = make_filepaths_from_dfs(JOINED_DIR, merged_dfs, '')
    n_saved = write_dfs_to_filepaths(merged_dfs, merged_fps)
    print(n_saved)


def join_dfs_within_seasons():
    left_source = 'football-data-co-uk'
    right_source = 'indatabet-com'
    sources = [left_source, right_source]
    join_within_league_seasons(sources)


if __name__ == "__main__":
    join_dfs_within_seasons()
