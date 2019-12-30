import pandas as pd
import numpy as np


def calc_rps_ss(rps: pd.Series, rps_b: pd.Series):
    """
    Accepts two Series - must be same length
    rps contains rank probability scores for individual events
    rps_b contains benchmark rank probability scores for individual events
    Return the Rank Probability Skill Score for each event as a Series
    """
    RPS_SS = 1 - (rps / rps_b)

    return RPS_SS


def calc_rps(pred_df: pd.DataFrame, obs_df: pd.DataFrame):
    """
    Accepts two DataFrames - DataFrames must be same size
    pred_df contains probability predictions of outcomes in ranked order
    obs_df contains 0 or 1 based on the observed outcome where the
    outcomes are in the same ranked order
    Return the Rank Probability Score for each row inside a series
    """
    pred_cdf = pred_df.cumsum(axis=1).values
    obs_cdf = obs_df.cumsum(axis=1).values

    return np.sum(1/(pred_df.shape[1]-1) * (pred_cdf - obs_cdf)**2, 1)


def calc_EVs(df_orig):
    df = df_orig.copy(deep=True)
    df['hwin_unit_EV'] = (df[1] * (df['hwinOdds']-1)) + ((1 - df[1]) * -1)
    df['draw_unit_EV'] = (df[2] * (df['drawOdds']-1)) + ((1 - df[2]) * -1)
    df['awin_unit_EV'] = (df[3] * (df['awinOdds']-1)) + ((1 - df[3]) * -1)
    return df


def select_bets(df_orig, threshold=0.1):
    df = df_orig.copy(deep=True)
    df[['hwin_bet', 'draw_bet', 'awin_bet']] = \
        df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']] >= threshold
    return df


def simulate_betting(df_orig):
    df = df_orig.copy(deep=True)

    conditions1 = [df['ordinal_result_1'] == 1,
                   df['ordinal_result_1'] == 0]
    choices1 = [(df['hwinOdds']-1) * df['hwin_bet'], -1 * df['hwin_bet']]
    df['hwin_rets'] = np.select(conditions1, choices1, default=0)

    conditions2 = [df['ordinal_result_2'] == 1,
                   df['ordinal_result_2'] == 0]
    choices2 = [(df['drawOdds']-1) * df['draw_bet'], -1 * df['draw_bet']]
    df['draw_rets'] = np.select(conditions2, choices2, default=0)

    conditions3 = [df['ordinal_result_3'] == 1,
                   df['ordinal_result_3'] == 0]
    choices3 = [(df['awinOdds']-1) * df['awin_bet'], -1 * df['awin_bet']]
    df['awin_rets'] = np.select(conditions3, choices3, default=0)
    df['game_ret'] = df[['hwin_rets', 'draw_rets', 'awin_rets']].sum(axis=1)
    return df
