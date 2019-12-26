import pathlib
import sys

import pandas as pd

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
                             drop_ha_nulls,
                             drop_duplicate_rows) # noqa E402

SCOPED_DIR = PROJECT_DIR / 'data' / '02-scoped'
CLEANED_DIR = PROJECT_DIR / 'data' / '03-cleaned'


def parse_dates(df_orig):
    df = df_orig.copy(deep=True)
    if 'bad' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], dayfirst=True)
    else:
        df['Date'] = pd.to_datetime(df['Date'])
    return df


def drop_unwanted_fdcuk_cols(df_orig):
    df = df_orig.copy(deep=True)
    unwanted_cols = ['Attendance', 'Country', 'Div', 'Season', 'Time', 'ABP',
                     'HBP', 'Referee', 'HTR', 'League', 'LB', 'LB.1', 'LB.2']
    df = df.drop(columns=unwanted_cols, errors='ignore')
    return df


def standardize_duplicate_col_names(df_orig):
    # Looks like there are differently named columns for the same thing
    # i.e Away, Away team and Home, Home Team
    # and for Goals AG and FTAG, and HG and FTHG
    df = df_orig.copy(deep=True)
    df.rename(columns={'AwayTeam': 'a', 'Away': 'a', 'HomeTeam': 'h',
                       'Home': 'h'}, inplace=True)
    df.rename(columns={'FTHG': 'h_ftGoals', 'HG': 'h_ftGoals'}, inplace=True)
    df.rename(columns={'FTAG': 'a_ftGoals', 'AG': 'a_ftGoals'}, inplace=True)
    df.rename(columns={'FTR': 'result', 'Res': 'result'}, inplace=True)

    df.rename(columns={'PSH': 'hwinOddsPinn', 'PH': 'hwinOddsPinn'},
              inplace=True)
    df.rename(columns={'PSD': 'drawOddsPinn', 'PD': 'drawOddsPinn'},
              inplace=True)
    df.rename(columns={'PSA': 'awinOddsPinn', 'PA': 'awinOddsPinn'},
              inplace=True)
    return df


def rename_fdcuk_cols(df_orig):
    """
    """
    df = df_orig.copy(deep=True)

    game_feature_cols = {'AC': 'a_corners', 'AR': 'a_redCards',
                         'AS': 'a_shots', 'AST': 'a_shotsOnTarget',
                         'AY': 'a_yellowCards', 'Date': 'date',
                         'HC': 'h_corners', 'HR': 'h_redCards',
                         'HS': 'h_shots', 'HST': 'h_shotsOnTarget',
                         'HY': 'h_yellowCards', 'HTAG': 'a_htGoals',
                         'HTHG': 'h_htGoals', 'AF': 'a_fouls', 'HF': 'h_fouls',
                         'HHW': 'h_woodWork', 'AHW': 'a_woodWork',
                         'AO': 'a_offsides', 'HO': 'h_offsides',
                         'AFKC': 'a_freeKicksConceded',
                         'HFKC': 'h_freeKicksConceded'}

    odds_cols = {'B365H': 'hwinOddsBet365', 'B365D': 'drawOddsBet365',
                 'B365A': 'awinOddsBet365', 'Bb1X2': 'n_Bb1X2',
                 'BbAH': 'n_BbAsian', 'BbAHh': 'BbAsianHandicap',
                 'BbAv<2.5': 'ftGoalsU2.5OddsBbMean',
                 'BbAv>2.5': 'ftGoalsO2.5OddsBbMean',
                 'BbAvA': 'awinOddsBbMean',
                 'BbAvAHA': 'oddsAsianAwayBbMean',
                 'BbAvAHH': 'oddsAsianHomeBbMean',
                 'BbAvD': 'drawOddsBbMean', 'BbAvH': 'hwinOddsBbMean',
                 'BbMx<2.5': 'ftGoalsU2.5OddsBbMax',
                 'BbMx>2.5': 'ftGoalsO2.5OddsBbMax', 'BbMxA': 'awinOddsBbMax',
                 'BbMxAHA': 'asianAwayOddsBbMax',
                 'BbMxAHH': 'asianHomeOddsBbMax', 'BbMxD': 'drawOddsBbMax',
                 'BbMxH': 'hwinOddsBbMax', 'BbOU': 'n_BbOU',
                 'IWH': 'hwinOddsIw', 'IWD': 'drawOddsIw', 'IWA': 'awinOddsIw',
                 'LBH': 'hwinOddsLb', 'LBD': 'drawOddsLb', 'LBA': 'awinOddsLb',
                 'PSCH': 'hwinClOddsPinn', 'PSCD': 'drawClOddsPinn',
                 'PSCA': 'awinClOddsPinn', 'VCH': 'hwinOddsVc',
                 'VCD': 'drawOddsVc', 'VCA': 'awinOddsVc',
                 'WHH': 'hwinOddsWh', 'WHD': 'drawOddsWh', 'WHA': 'awinOddsWh',
                 'MaxH': 'hwinOddsMarketMax', 'MaxD': 'drawOddsMarketMax',
                 'MaxA': 'awayOddsMarketMax', 'AvgH': 'hwinOddsMarketMean',
                 'AvgD': 'drawOddsMarketMean', 'AvgA': 'awayOddsMarketMean',
                 'B365AH': 'hHandicapSizeBet365',
                 'B365AHA': 'aAsianHandicapOddsBet365',
                 'B365AHH': 'hAsianhandicapOddsBet365',
                 'BSA': 'awinOddsBsa', 'BSD': 'drawOddsBsa',
                 'BSH': 'hwinOddsBsa', 'BWA': 'awinOddsBwa',
                 'BWD': 'drawOddsBwa', 'BWH': 'hwinOddsBwa',
                 'GBH': 'hwinOddsGb', 'GBD': 'drawOddsGb', 'GBA': 'awinOddsGb',
                 'SBA': 'awinOddsSb', 'SBD': 'drawOddsSb', 'SBH': 'hwinOddsSb',
                 'SJA': 'awinOddsSj', 'SJD': 'drawOddsSj', 'SJH': 'hwinOddsSj',
                 'SOA': 'awinOddsSo', 'SOD': 'drawOddsSo', 'SOH': 'hwinOddsSo',
                 'SYA': 'awinOddsSy', 'SYD': 'drawOddsSy', 'SYH': 'hwinOddsSy',
                 'GBAH': 'hHandicapSizeGb',
                 'GBAHA': 'aAsianHandicapOddsGb',
                 'GBAHH': 'hAsianHandicapOddsGb',
                 'LBAH': 'hhandicapSizeLb', 'LBAHA': 'aAsianHandicapOddsLb',
                 'LBAHH': 'hAsianHandicapOddsLb',
                 'B365<2.5': 'ftGoalsU2.5OddsBet365',
                 'B365>2.5': 'ftGoalsO2.5OddsBet365',
                 'GB<2.5': 'ftGoalsU2.5OddsGb',
                 'GB>2.5': 'ftGoalsO2.5OddsGb'}

    df.rename(columns=game_feature_cols, inplace=True)
    df.rename(columns=odds_cols, inplace=True)
    return df


def drop_awarded(df_orig):
    df = df_orig.copy(deep=True)

    # if nation, league, season, h, a:
    #     drop row

    return df


def clean_up_dfs(dfs):
    clean_dfs = []
    for df in dfs:
        df = drop_unnamed(df)
        df = parse_dates(df)
        df = drop_all_nulls(df, axis=1)
        df = drop_all_nulls(df, axis=0)
        df = drop_ha_nulls(df)
        df = drop_unwanted_fdcuk_cols(df)
        df = standardize_duplicate_col_names(df)
        df = rename_fdcuk_cols(df)
        df = make_results_col(df)
        df = lowercase_team_names(df)
        df = drop_duplicate_rows(df)
        df = drop_awarded(df)
        clean_dfs.append(df)
    return clean_dfs


def clean_football_data_co_uk():
    filepaths = get_filepaths(SCOPED_DIR / 'football-data-co-uk', ext='csv')
    dfs = read_csvs_to_dfs(filepaths)
    clean_dfs = clean_up_dfs(dfs)
    cleaned_fps = make_filepaths_from_dfs(CLEANED_DIR,
                                          clean_dfs,
                                          data_origin='football-data-co-uk')
    n_saved = write_dfs_to_filepaths(clean_dfs, cleaned_fps)
    print(n_saved)


if __name__ == "__main__":
    clean_football_data_co_uk()
