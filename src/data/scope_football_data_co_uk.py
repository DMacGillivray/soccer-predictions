import pathlib

import pandas as pd

from pfuncs import load_pickle, make_filepaths_from_dfs, write_dfs_to_filepaths

PROJECT_DIR = pathlib.Path().cwd().resolve()

SCOPE_DICT_DIR = PROJECT_DIR / 'data' / 'reference' / 'scope-dict'
RAW_DIR = PROJECT_DIR / 'data' / '01-raw'
SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'


def make_fdcuk_filepaths(top_level_dir, scope_dict):
    """
    Accepts a parent filepath - pathlib Path object and
    a scope dictionary
    Uses these to make filepaths for rge football-data-co-uk data
    in the raw data repository
    """
    filepaths = []
    for nation, league in zip(scope_dict['nations'], scope_dict['leagues']):
        for season in scope_dict['seasons']:
            filename = season + '.csv'
            stub = top_level_dir / 'football-data' / nation / league / season
            filepath = stub / 'football-data-co-uk' / 'season-data' / filename
            if filepath.exists():
                filepaths.append(filepath)
    return filepaths


def add_fdcuk_meta_data(df, filepath):
    """
    Accepts a dataframe and a filepath
    parses the filepath to get strings representing
    nation, league, and season
    writes this data to the dataframe
    Returns the changed dataframe
    """
    season = filepath.stem
    str_filepath = str(filepath)
    str_filepath_parts = str_filepath.split('/')
    nation = str_filepath_parts[11]
    league = str_filepath_parts[12]
    df['nation'] = nation
    df['league'] = league
    df['season'] = season
    return df


def read_badly_formed_csv_to_df(filepath):
    """
    https://stackoverflow.com/questions/55188544/pandas-how-to-workaround-error-tokenizing-data

    """
    df = pd.read_csv(filepath, header=None, sep='\n', encoding='ISO-8859-1')
    df = df[0].str.split(',', expand=True)
    df.columns = df.iloc[0]
    df.drop([0], axis=0, inplace=True)
    df = add_fdcuk_meta_data(df, filepath)
    # Mark this dataframe as "bad" because we need to catch it later
    # to do some special processing
    df['bad'] = 1
    return df


def load_fdcuk_filepaths_as_dfs(filepaths):
    good_dfs = []
    bad_dfs = []
    for filepath in filepaths:
        try:
            df = pd.read_csv(filepath,
                             dayfirst=True,
                             parse_dates=['Date'],
                             engine='python',
                             error_bad_lines=True,
                             encoding='ISO-8859-1')
            df = add_fdcuk_meta_data(df, filepath)
            good_dfs.append(df)
        except pd.errors.ParserError:
            df = read_badly_formed_csv_to_df(filepath)
            bad_dfs.append(df)
    dfs = good_dfs + bad_dfs
    return dfs


def scope_football_data_co_uk():
    scope_dict = load_pickle(SCOPE_DICT_DIR)
    fdcuk_fps = make_fdcuk_filepaths(RAW_DIR, scope_dict)
    all_season_dfs = load_fdcuk_filepaths_as_dfs(fdcuk_fps)

    scoped_fps = make_filepaths_from_dfs(SCOPED_DIR,
                                         all_season_dfs,
                                         data_origin='football-data-co-uk')
    n_saved = write_dfs_to_filepaths(all_season_dfs, scoped_fps)
    print(n_saved)


if __name__ == "__main__":
    scope_football_data_co_uk()
