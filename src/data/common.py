import pathlib
import pickle

import pandas as pd
from pyxlsb import open_workbook as open_xlsb

def load_pickle(parent_dir):
    """
    Accepts a parent directory Path object
    which can contain only one pickled file with a .pkl extension
    Finds the file, loads it, and returns it
    """
    filepath = list(parent_dir.glob('*.pkl'))[0]
    print(filepath)
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
        filepath = top_dest_dir / data_origin / nation / league / season / filename
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

def pandas_read_xlsb_file(filepath):
    """
    https://stackoverflow.com/questions/45019778/read-xlsb-file-in-pandas-python
    Accepts a filepath - pathlib.Path object
    Reads an xlsb file into a dataframe
    Returns the dataframe
    """
    dfs = []
    with open_xlsb(filepath) as wb:
        with wb.get_sheet(1) as sheet:
            for row in sheet.rows():
                dfs.append([item.v for item in row])
    df = pd.DataFrame(dfs[1:], columns=dfs[0])
    return df

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
        # Where there are abandoned matches or penalty finishes this fails
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
        df[col] = df[col].str.lower().str.replace(' ', '-').str.replace('.','')
    return df

def drop_unnamed(df_orig):
    df = df_orig.copy(deep=True)
    drop_cols = [col for col in df.columns if 'Unnamed' in col]
    df.drop(columns = drop_cols, inplace=True)    
    return df

def parse_dates(df_orig):
    df = df_orig.copy(deep=True)
    if 'bad' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    else:
        df['Date'] = pd.to_datetime(df['Date'])    
    return df

def drop_all_nulls(df_orig, axis=1):
    df = df_orig.copy(deep=True)
    # Drop any columns that are all null
    df = df_orig.dropna(axis=axis, how='all')
    return df

def make_equiv_image_dest_fps(src_top_level_dir, dest_top_level_dir, src_fps):
    # src looks like
    # '/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data/
    # 02-scoped/whoscored-com-heatmaps/england/english-premier-league/2009-2010/Arsenal__Aston Villa.png
    
    # dest shoulkd look like
    #'/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data
    #/02-cleaned/whoscored-com-heatmaps/germany/bundesliga/2009-2010/Bayern__Bochum.png'
    orig_dir = str(src_top_level_dir).split('/')[-1]
    new_dir = str(dest_top_level_dir).split('/')[-1]
    dest_fps = []
    for src_fp in src_fps:
        dest_fp = pathlib.Path(str(src_fp).replace(orig_dir, new_dir))
        dest_fps.append(dest_fp)
        
    return dest_fps

def get_std_dict_from_path(fp, std_dict_top_dir):
    #'/media/david/5C14F53A14F517AA/code/ana_py37/projects/soccer-predictions/data/
    #03-cleaned/whoscored-com-shotmaps/england/english-premier-league/2009-2010/Arsenal__Aston Villa.png')
    fp_parts = str(fp).split('/')
    nation = fp_parts[-4]
    league = fp_parts[-3]
    fn = league + '.pkl'
    fp = std_dict_top_dir / nation / league / fn
    try:
        with open(fp, 'rb') as handle:
            std_dict = pickle.load(handle)
    except:
        std_dict = {'key':'value'}
    return std_dict

def standardize_team_names(df_orig, std_names_dict):
    """
    """
    df = df_orig.copy(deep=True)
    
    # If there is no standard dictioanry available yet, return an empty dataframe
    # so that we don't write a non-standardized dataframe to the standardized directory
    if std_names_dict == {'key':'value'}:
        df = pd.DataFrame()
    else:
        # Standardize the team names
        df['h'] = df['h'].str.strip().str.lower().str.replace(' ', '-')
        df.loc[df['h'].isin(std_names_dict.keys()), 'h'] = df['h'].map(std_names_dict)
        df['a'] = df['a'].str.strip().str.lower().str.replace(' ', '-')
        df.loc[df['a'].isin(std_names_dict.keys()), 'a'] = df['a'].map(std_names_dict)
        if df['h'].isnull().sum() + df['a'].isnull().sum() > 0:
            print(df.head(2))
    return df

def standardize_dfs(dfs, std_dict_top_dir):
    """
    """
    stdzed_dfs = []
    for df in dfs:
        std_dict = get_std_dict_from_path(df, std_dict_top_dir)
        df = standardize_team_names(df, std_dict)
        stdzed_dfs.append(df)
    return stdzed_dfs
