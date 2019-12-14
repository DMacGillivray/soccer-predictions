import pathlib
import pickle

import pandas as pd

from pfuncs import (get_filepaths,
                    read_csvs_to_dfs,
                    write_dfs_to_filepaths,
                    make_filepaths_from_dfs)

PROJECT_DIR = pathlib.Path().cwd().resolve()
CLEANED_DIR = PROJECT_DIR / 'data' / '03-cleaned'
STDZED_DIR = PROJECT_DIR / 'data' / '04-standardized'
REF_DIR = PROJECT_DIR / 'data' / 'reference'


def get_std_dict_from_df(df, std_dict_top_dir):
    """
    """
    nation = df['nation'].unique()[0]
    league = df['league'].unique()[0]
    fn = league + '.pkl'
    fp = std_dict_top_dir / nation / league / fn

    try:
        with open(fp, 'rb') as handle:
            std_dict = pickle.load(handle)
        return std_dict
    except IOError:
        return {'key': 'value'}


def standardize_team_names(df_orig, std_names_dict):
    """
    """
    df = df_orig.copy(deep=True)

    # If there is no standard dictioanry available yet, return an empty
    # dataframe so that we don't write a non-standardized dataframe
    # to the standardized directory
    if std_names_dict == {'key': 'value'}:
        df = pd.DataFrame()
    else:
        # Standardize the team names
        df['h'] = df['h'].str.strip().str.lower().str.replace(' ', '-')
        df.loc[df['h'].isin(std_names_dict.keys()), 'h'] = \
            df['h'].map(std_names_dict)
        df['a'] = df['a'].str.strip().str.lower().str.replace(' ', '-')
        df.loc[df['a'].isin(std_names_dict.keys()), 'a'] = \
            df['a'].map(std_names_dict)
        if df['h'].isnull().sum() + df['a'].isnull().sum() > 0:
            pass
            # print(df.head(2))
    return df


def standardize_dfs(dfs, std_dict_top_dir):
    """
    """
    stdzed_dfs = []
    for df in dfs:
        std_dict = get_std_dict_from_df(df, std_dict_top_dir)
        df = standardize_team_names(df, std_dict)
        stdzed_dfs.append(df)
    return stdzed_dfs


def standardize_df_team_names(source_dir):
    filepaths = get_filepaths(CLEANED_DIR / source_dir, ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    stdzed_dfs = standardize_dfs(dfs, REF_DIR)
    # Not all standardized dictionaries available yet
    stdzed_dfs = [df for df in stdzed_dfs if len(df) > 0]
    stdzed_dfs_fps = make_filepaths_from_dfs(STDZED_DIR,
                                             stdzed_dfs,
                                             source_dir)
    n_saved = write_dfs_to_filepaths(stdzed_dfs, stdzed_dfs_fps)
    print(n_saved)


if __name__ == "__main__":
    for source_dir in ['football-data-co-uk', 'indatabet-com']:
        standardize_df_team_names(source_dir)
