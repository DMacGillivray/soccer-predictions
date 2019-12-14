import pathlib

import pandas as pd
from pyxlsb import open_workbook as open_xlsb

from pfuncs import load_pickle, make_filepaths_from_dfs, write_dfs_to_filepaths

PROJECT_DIR = pathlib.Path().cwd().resolve()

SCOPE_DICT_DIR = PROJECT_DIR / 'data' / 'reference' / 'scope-dict'
RAW_DIR = PROJECT_DIR / 'data' / '01-raw'
SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'
INDATABET_FILEPATH = (RAW_DIR / 'indatabet-free-download' /
                      'oOo FT_2in1_Pinnacle & bet365_ML TG_01 April 2019.xlsb')


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


def clean_monolithic_df(df_orig):
    """
    Have to do some cleaning in order to split
    """
    df = df_orig.copy(deep=True)
    # Cutoff columns
    df = df.iloc[:, 0:35]
    # make column names strings
    col_mapper = {col: str(col) for col in df.columns}
    df.rename(columns=col_mapper, inplace=True)
    df.columns = df.columns.str.lower()
    # Drop unnecessary columns
    # Columns that can be calculated from other data
    # such as Results goals over, under etc
    # col 12 is first None | R | none
    drop_cols = set([12, 13, 14, 15, 16, 17, 20, 21, 26, 30])
    all_cols = set(range(0, df.shape[1]))
    keeper_cols = all_cols.difference(drop_cols)
    df = df.iloc[:, list(keeper_cols)]
    col_names = ['yy', 'dd', 'mm', 'date', 'id_fifa', 'country', 'league',
                 'season', 'h', 'a', 'h_htgoals', 'a_htgoals', 'h_ftGoals',
                 'a_ftGoals', 'et_pen_awd',
                 'odds_hwin_pinn', 'odds_draw_pinn', 'odds_awin_pinn',
                 'odds_hwin_bet365', 'odds_draw_bet365', 'odds_awin_bet365',
                 'odds_ftgoalso2.5_pinn', 'odds_ftgoalsu2.5_pinn',
                 'odds_ftgoalso2.5_bet365', 'odds_ftgoalsu2.5_bet365']
    df.columns = col_names
    df = df.iloc[2:].reset_index(drop=True)
    # Put seasons into my format
    df['season'] = df['season'].str.replace('/', '-')
    # Format column data to lower case strings, replace  space with dash
    str_cols = df.columns[(df.applymap(type) == str).all(0)]
    for col in str_cols:
        df[col] = df[col].str.strip().str.lower().str.replace(' ', '-')

    # Assemble date into common format - original date column cannot be trusted
    #  - multiple formats
    df['date'] = pd.to_datetime(df['yy'].astype(int).astype(str) +
                                '-' + df['mm'].astype(str)
                                + '-' + df['dd'].astype(int).astype(str))
    df.drop(columns=['yy', 'dd', 'mm'], inplace=True)
    df.sort_values(by='date', ascending=True, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df


def scope_monolithic_df(monolithic_df, scope_dict):
    season_dfs = []
    for nation, league in zip(scope_dict['nations'], scope_dict['leagues']):
        for season in scope_dict['seasons']:
            crit1 = monolithic_df['nation'] == nation
            crit2 = monolithic_df['league'] == league
            crit3 = monolithic_df['season'] == season
            season_df = monolithic_df[crit1 & crit2 & crit3]
            if len(season_df):
                season_dfs.append(season_df)
    return season_dfs


def prep_monolithic_for_scoping(monolithic_df):
    df = monolithic_df.copy(deep=True)

    df.rename(columns={'country': 'nation'}, inplace=True)
    crit1 = df['nation'] == 'england'
    crit2 = df['league'] == 'premier-league'
    df.loc[crit1 & crit2, 'league'] = 'english-premier-league'

    crit3 = df['league'] == 'championship'
    df.loc[crit1 & crit3, 'league'] = 'english-championship'

    crit4 = df['league'] == 'league-one'
    df.loc[crit1 & crit4, 'league'] = 'one'

    crit5 = df['nation'] == 'germany'
    crit6 = df['league'] == '2.-bundesliga'
    df.loc[crit5 & crit6, 'league'] = 'bundesliga-2'

    crit7 = df['nation'] == 'spain'
    crit8 = df['league'] == 'primera-division'
    df.loc[crit7 & crit8, 'league'] = 'la-liga'

    return df


def scope_indatabet_com():
    scope_dict = load_pickle(SCOPE_DICT_DIR)
    df_raw = pandas_read_xlsb_file(INDATABET_FILEPATH)
    df_clean = clean_monolithic_df(df_raw)
    df_prepped = prep_monolithic_for_scoping(df_clean)
    scoped_dfs = scope_monolithic_df(df_prepped, scope_dict)
    scoped_fps = make_filepaths_from_dfs(SCOPED_DIR,
                                         scoped_dfs,
                                         data_origin='indatabet-com')
    n_saved = write_dfs_to_filepaths(scoped_dfs, scoped_fps)
    print(n_saved)


if __name__ == "__main__":
    scope_indatabet_com()
