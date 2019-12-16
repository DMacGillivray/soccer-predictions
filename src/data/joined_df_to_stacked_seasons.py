import pathlib

import pandas as pd

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    get_actual_scope_dict)

PROJECT_DIR = pathlib.Path().cwd().resolve()
JOINED_DIR = PROJECT_DIR / 'data' / '05-joined'
STACKED_DIR = PROJECT_DIR / 'data' / '06-stacked-seasons'


def get_df_seasons(df):
    seasons = sorted(df['season'].unique().tolist())
    return seasons


def stackseasons():
    filepaths = get_filepaths(JOINED_DIR)
    actual_scope_dict = get_actual_scope_dict(filepaths)

    n_written = 0
    stacked_leagues = []
    stacked_filepaths = []
    for nation, league in zip(actual_scope_dict['nations'],
                              actual_scope_dict['leagues']):
        league_seasons = [fp for fp in filepaths if nation in str(fp)
                          and league in str(fp)]
        league_seasons_dfs = read_csvs_to_dfs(league_seasons)
        league_season_df = pd.concat(league_seasons_dfs, axis=0, sort=True)
        league_season_df.sort_values(by=['season', 'date'], inplace=True)
        league_season_df.reset_index(drop=True, inplace=True)
        stacked_leagues.append(league_season_df)

        seasons = get_df_seasons(league_season_df)
        fn = seasons[0] + '__' + seasons[-1] + '.csv'
        save_path = STACKED_DIR / nation / league / fn
        stacked_filepaths.append(save_path)

    n_written = write_dfs_to_filepaths(stacked_leagues, stacked_filepaths)
    print(n_written)


if __name__ == "__main__":
    stackseasons()
