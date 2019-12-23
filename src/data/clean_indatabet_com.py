import pathlib
import sys

PROJECT_DIR = pathlib.Path.cwd().resolve()
sys.path.append(str(PROJECT_DIR))

from src.data.pfuncs import (get_filepaths,
                             read_csvs_to_dfs,
                             make_filepaths_from_dfs,
                             drop_unnamed,
                             drop_all_nulls,
                             make_results_col,
                             lowercase_team_names,
                             write_dfs_to_filepaths,
                             drop_duplicate_rows) # noqa E402

PROJECT_DIR = pathlib.Path().cwd().resolve()

SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'
CLEANED_DIR = PROJECT_DIR / 'data' / '03-cleaned'


def rename_indatabet_cols(df_orig):
    """
    """
    df = df_orig.copy(deep=True)

    odds_cols = {'odds_awin_pinn': 'awinOddsPinnIndatabet',
                 'odds_draw_pinn': 'drawOddsPinnIndatabet',
                 'odds_hwin_pinn': 'hwinOddsPinnIndatabet',
                 'odds_awin_bet365': 'awinOddsBet365Indatabet',
                 'odds_draw_bet365': 'drawOddsBet365Indatabet',
                 'odds_hwin_bet365': 'hwinOddsBet365Indatabet',
                 'odds_ftgoalso2.5_bet365': 'ftGoalsO2.5OddsBet365Indatabet',
                 'odds_ftgoalsu2.5_bet365': 'ftGoalsU2.5OddsBet365Indatabet',
                 'odds_ftgoalso2.5_pinn': 'ftGoalsO2.5OddsPinnIndatabet',
                 'odds_ftgoalsu2.5_pinn': 'ftGoalsU2.5OddsPinnIndatabet'}

    df.rename(columns=odds_cols, inplace=True)
    return df


def clean_special_cases(df_orig):
    df = df_orig.copy(deep=True)
    # Apply to all make a 1,1 draw
    if 'et_pen_awd' in df.columns:
        if df['et_pen_awd'].isnull().sum() > 0:
            # crit = df['et_pen_awd'].isnull()
            idx = df[~df['et_pen_awd'].isnull()].index
            df.loc[idx, ['h_ftGoals', 'a_ftGoals']] = [1.0, 0.0]
    df[['h_ftGoals', 'a_ftGoals']] = \
        df[['h_ftGoals', 'a_ftGoals']].astype(float)
    return df


def clean_up_dfs(dfs):
    clean_dfs = []
    for df in dfs:
        df = drop_unnamed(df)
        df = drop_all_nulls(df, axis=1)
        df = drop_all_nulls(df, axis=0)
        df = rename_indatabet_cols(df)
        df = lowercase_team_names(df)
        df = drop_duplicate_rows(df)
        df = clean_special_cases(df)
        # after dealing with special cases
        # because this is a merge column
        df = make_results_col(df)
        clean_dfs.append(df)
    return clean_dfs


def clean_indatabet_com():
    filepaths = get_filepaths(SCOPED_DIR / 'indatabet-com', ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    clean_dfs = clean_up_dfs(dfs)
    cleaned_fps = make_filepaths_from_dfs(CLEANED_DIR,
                                          clean_dfs,
                                          data_origin='indatabet-com')
    n_saved = write_dfs_to_filepaths(clean_dfs, cleaned_fps)
    print(n_saved)


if __name__ == "__main__":
    clean_indatabet_com()
