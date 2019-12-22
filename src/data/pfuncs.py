import pathlib
import pickle

import pandas as pd
import numpy as np


def get_nations(filepaths):
    nations = list(np.unique([str(fp).split('/')[-4] for fp in filepaths]))
    return nations


def get_nations_leagues(filepaths, nations):
    expanded_nations = []
    leagues = []
    for nation in nations:
        national_leagues = list(np.unique([str(fp).split('/')[-3] for
                                fp in filepaths if nation in str(fp)]))
        expanded_nations.extend([nation] * len(national_leagues))
        leagues.extend(national_leagues)
    return expanded_nations, leagues


def get_seasons(filepaths):
    seasons = sorted(list(np.unique([str(fp).split('/')[-2] for
                                     fp in filepaths])))
    return seasons


def get_actual_scope_dict(filepaths):
    nations = get_nations(filepaths)
    nations, leagues = get_nations_leagues(filepaths, nations)
    possible_seasons = get_seasons(filepaths)
    actual_scope_dict = {'nations': nations,
                         'leagues': leagues,
                         'seasons': possible_seasons}
    return actual_scope_dict


def load_pickle(parent_dir):
    """
    Accepts a parent directory Path object
    which can contain only one pickled file with a .pkl extension
    Finds the file, loads it, and returns it
    """
    # print(parent_dir)
    filepath = list(parent_dir.glob('*.pkl'))[0]
    with open(str(filepath), 'rb') as f:
        data = pickle.load(f)
    return data


def make_filepaths_from_dfs(top_dest_dir, dfs, data_origin):
    """
    Accepts:
     - a parent directory - top_dest_dir as a Path object
     - a list of dataframes - dfs
       containing columns and data for nation, league and season
     - a string representing the original source of the data
     Returns a list of filepaths associated with each dataframe
    """
    filepaths = []
    for df in dfs:
        nation = df['nation'].unique()[0]
        league = df['league'].unique()[0]
        season = df['season'].unique()[0]
        filename = str(season) + '.csv'
        filepath = (top_dest_dir / data_origin / nation / league /
                    season / filename)
        filepaths.append(filepath)
    return filepaths


def write_dfs_to_filepaths(dfs, filepaths):
    """
    Accepts a list of pandas dataframes - dfs
    and a parralel list of filepaths - pathlib path objects
    Writes the dataframes to the filepaths as csvs with no index
    Returns the number of files written integer
    """
    n = 0
    for df, filepath in zip(dfs, filepaths):
        if not filepath.exists():
            filepath.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(filepath, index=False)
        n += 1
    return n


def copy_files(src_filepaths, dest_filepaths):
    """
    Accepts two parallel lists of pathlib Path objects - full filepaths
    Copies the files
    Creates the destination directory if it does not already exist
    Returns the number of files copied - integer
    """
    n_copied = 0
    for src_filepath, dest_filepath in zip(src_filepaths, dest_filepaths):
        if not dest_filepath.exists():
            dest_filepath.parent.mkdir(parents=True, exist_ok=True)
        dest_filepath.write_bytes(src_filepath.read_bytes())
        n_copied += 1
    return n_copied


def get_filepaths(parent_dir, ext='csv'):
    """
    Accepts a parent directory filepath - pathlib.Path object
    and a string representing a file extension
    Recursivley finds all files with that extension below the parent filepath
    Returns a list of all filepaths as pathlib.Path objects
    """
    filepaths = list(parent_dir.rglob('*.' + ext))
    return filepaths


def read_csvs_to_dfs(filepaths):
    """
    Accepts a list of filepaths pointing to a csv file
    Loads each csv into a dataframe
    Returns a parallel list of dataframes
    """
    dfs = [pd.read_csv(filepath) for filepath in filepaths]
    return dfs


def make_results_col(df_orig):
    """
    Accepts a dataframe containing columns
    home full time goals and away ft goals
    h_ftGoals, a_ftGoals
    enumerates the match results into a column named results
    as hwin, draw, awin
    Returns amended dataframe
    COMMON !!!!!!!!!!!!!!!!!!!!!!!!
    """
    df = df_orig.copy(deep=True)
    # print(df['nation'].unique())
    # print(df['league'].unique())
    # print(df['season'].unique())
    try:
        if 'result' in df.columns:
            df.drop(columns=['result'], inplace=True)
        # Calculate Results column
        conditions = [df['h_ftGoals'] > df['a_ftGoals'],
                      df['h_ftGoals'] == df['a_ftGoals'],
                      df['h_ftGoals'] < df['a_ftGoals']]
        choices = ['hwin', 'draw', 'awin']
        df['result'] = np.select(conditions, choices, default='not-played')
    except:
        #  Where there are abandoned matches or penalty finishes this fails
        df['result'] = None
    return df


def lowercase_team_names(df_orig):
    """
    Accepts a Dataframe with columns h and a
    representing home and away team names with strings
    makes these team names lowercase, replaces spaces with dashes,
    and strips out dots
    Returns the amended dataframe
    """
    df = df_orig.copy(deep=True)
    for col in ['h', 'a']:
        df[col] = df[col].str.lower().str.replace(' ', '-').\
            str.replace('.', '')
    return df


def drop_unnamed(df_orig):
    df = df_orig.copy(deep=True)
    drop_cols = [col for col in df.columns if 'Unnamed' in col]
    df.drop(columns=drop_cols, inplace=True)
    return df


def drop_all_nulls(df_orig, axis=1):
    df = df_orig.copy(deep=True)
    # Drop any columns that are all null
    df = df.dropna(axis=axis, how='all')
    return df


def drop_ha_nulls(df_orig):
    df = df_orig.copy(deep=True)
    # Drop any rows where the home team and away team are not defined
    if 'HomeTeam' in df.columns:
        df = df.dropna(subset=['HomeTeam', 'AwayTeam'], axis=0)
    if 'Home' in df.columns:
        df = df.dropna(subset=['Home', 'Away'], axis=0)
    return df


def drop_duplicate_rows(df_orig):
    df = df_orig.copy()
    df.drop_duplicates(inplace=True)
    return df


def make_equiv_image_dest_fps(src_top_level_dir, dest_top_level_dir, src_fps):
    # src looks like
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data/
    # 02-scoped/whoscored-com-heatmaps/england/english-premier-league/
    # 2009-2010/Arsenal__Aston Villa.png
    # dest should look like
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data
    # /02-cleaned/whoscored-com-heatmaps/germany/bundesliga/2009-2010/Bayern__Bochum.png'
    orig_dir = str(src_top_level_dir).split('/')[-1]
    new_dir = str(dest_top_level_dir).split('/')[-1]
    dest_fps = []
    for src_fp in src_fps:
        dest_fp = pathlib.Path(str(src_fp).replace(orig_dir, new_dir))
        dest_fps.append(dest_fp)
    return dest_fps


def get_matching_filepaths(left_df_fps,
                           right_df_fps,
                           left_source,
                           right_source):
    left_fps = [fp for fp in left_df_fps if
                pathlib.Path(str(fp).replace(left_source, right_source))
                in right_df_fps]
    right_fps = [fp for fp in right_df_fps if
                 pathlib.Path(str(fp).replace(left_source, right_source))
                 in right_df_fps]
    return left_fps, right_fps
