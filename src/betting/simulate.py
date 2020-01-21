import numpy as np
import pandas as pd

def bet_all_positive_EVs(df_orig, param_dict={'EV_threshold': 0.0}):
    df = df_orig.copy(deep=True)
    # # Betting Strategy # 1
    # # ## EV > Threshold ##
    EV_threshold = param_dict['EV_threshold']
    mask = (df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']] >= EV_threshold).values
    df[['hwin_bet', 'draw_bet', 'awin_bet']] = pd.DataFrame(mask)
    return df


def bet_highest_EV_per_game(df_orig, param_dict={'EV_threshold': 0.0}):
    # Betting Strategy # 2
    ## EV > Threshold - Bet on Maximum EV for each Game ##
    df = df_orig.copy(deep=True)
    EV_threshold = param_dict['EV_threshold']
    mask1 = (df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']] >= EV_threshold).values
    mask2 = df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']].values.max(axis=1,keepdims=1) == \
                df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']].values

    mask = np.logical_and(mask1, mask2)
    df[['hwin_bet', 'draw_bet', 'awin_bet']] = pd.DataFrame(mask)
    return df


def bet_single_type_positive_EV(df_orig, param_dict={'EV_threshold': 0.0, 'bet_type': 'hwin'}):    
    # # Betting Strategy # 4
    # ## EV > Threshold - Bet on Maximum EV for each Game, only bet on draws##
    # EV_threshold = 0.1
    df = df_orig.copy(deep=True)
    EV_threshold = param_dict['EV_threshold']
    bet_type = param_dict['bet_type']
    mask1 = (df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']] >= EV_threshold).values
    mask2 = df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']].values.max(axis=1,keepdims=1) == \
                 df[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']].values

    mask = np.logical_and(mask1, mask2)
    if bet_type == 'hwin':
        mask[:,1] = 0
        mask[:,2] = 0
    if bet_type == 'draw':
        mask[:,0] = 0
        mask[:,2] = 0
    if bet_type == 'awin':
        mask[:,0] = 0
        mask[:,1] = 0
    df[['hwin_bet', 'draw_bet', 'awin_bet']] = pd.DataFrame(mask)
    return df


def bet_EV_threshold_odds_threshold(df_orig, params_dict):
    df = df_orig.copy(deep=True)
    # # Betting Strategy # 5
    # # ## EV > EV_Threshold - Odds < odds_threshold ##
    # EV_threshold = 0.1
    # odds_threshold = 6.0

    # mask1 = (df_test[['hwin_unit_EV', 'draw_unit_EV', 'awin_unit_EV']] >= EV_threshold).values
    # mask2 = (df_test[['hwinOddsMean', 'drawOddsMean', 'awinOddsMean']] <= odds_threshold).values

    # mask = np.logical_and(mask1, mask2)

    # df_test['hwin_bet'] = 0 ; df_test['draw_bet'] = 0 ; df_test['awin_bet'] = 0
    # df_test[['hwin_bet', 'draw_bet', 'awin_bet']] = mask
    return df


def do_bets(df_orig):
    df = df_orig.copy(deep=True)

    # Do betting
    for n, bet_type in zip([1, 2, 3], ['hwin', 'draw', 'awin']):
        # Condition 1 - Place bet and bet wins
        # Condition 2 - Place bet and bet loses
        conditions = [(df[bet_type + '_bet'] == 1) & (df['ordinal_result_' + str(n)] == 1),
                      (df[bet_type + '_bet'] == 1) & (df['ordinal_result_' + str(n)] == 0)]
        # Choices - 1 - Winnings; 2 - Loss
        choices = [(df[bet_type + 'OddsMax']-1), -1]
        # Default - no bet placed
        df[bet_type +'_rets'] = np.select(conditions, choices, default=0)
        
    # Works if placing a single bet [per game]
    def get_placed_bet(row):
        if row[0]:
            return 'hwin_bet'
        elif row[1]:
            return 'draw_bet'
        elif row[2]:
            return 'awin_bet'
        else:
            return 'no_bet'
    df['placed_bet'] = df[['hwin_bet', 'draw_bet', 'awin_bet']].apply(get_placed_bet, axis=1)

    # Get total Return per Game
    df['game_ret'] = df[['hwin_rets', 'draw_rets', 'awin_rets']].sum(axis=1)
    
    return df
        
        
def calculate_EVs(df_orig):
    df = df_orig.copy(deep=True)
    df['hwin_unit_EV'] = (df[1]* (df['hwinOddsMean']-1)) + ((1- df[1]) * -1)
    df['draw_unit_EV'] = (df[2]* (df['drawOddsMean']-1)) + ((1- df[2]) * -1)
    df['awin_unit_EV'] = (df[3]* (df['awinOddsMean']-1)) + ((1- df[3]) * -1)
    return df
    
    
def simulate_betting(df,
                     strategy='highest_EV_per_game',
                     param_dict={'EV_threshold': 0.0, 'bet_type': 'hwin'}):
    
    df = calculate_EVs(df)
    
    if strategy == 'highest_EV_per_game':
        df = bet_highest_EV_per_game(df, param_dict)
    if strategy == 'all_positive_EVs':
        df = bet_all_positive_EVs(df, param_dict)
    if strategy == 'single_bet_type_positive_EV':
        df = bet_single_type_positive_EV(df, param_dict)
        
    df = do_bets(df)
    return df
# 