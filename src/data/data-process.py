# -*- coding: utf-8 -*-
import operator
import pathlib
import numpy as np
import pandas as pd

def form_teams_records(df,
                       team_location='h',
                       records='h',
                       feature = 'ftgoals'):
    """
    Accept a league table of matches with a feature
    """
    team_records = []
    for _, team_df in df.groupby(by=team_location):
        lags = range(0, len(team_df))
        records_df = pd.DataFrame({f'{team_location}_{records}_{feature}-{n}':
                                  team_df[team_location + '_' + feature].shift(n) for n in lags})
        team_record = pd.concat([team_df, records_df], axis=1)
        team_records.append(team_record)
        # print(team_record)
    full_df = pd.concat(team_records, axis=0).sort_index()
    print(full_df)
    return full_df

def form_teams_records_(df,
                       team_location='h',
                       records='a',
                       feature = 'ftgoals'):
    """
    Accept a league table of matches with a feature
    """
    #cols = [team_location, records + '_' + feature]
    #grouped = df.groupby(by=team_location)
    location_indices = [list(df.index) for _, df in df.groupby(by=team_location)]
    # print(location_indices)
    records_indices = [list(df.index) for _, df in df.groupby(by=records)]
    # print(records_indices)
    # #lags = [loc_inds[loc_inds < n].max() for n in rec_inds for (loc_inds, rec_inds) in zip(location_indices, records_indices)]
    lags0 = [list(map(lambda x: x+1,list(map(operator.sub, loc_inds, rec_inds)))) for (loc_inds, rec_inds) in zip(location_indices, records_indices)]
    # #lags = [loc_inds[loc_inds< n].max() for n in rec_inds for (loc_inds, rec_inds) in zip(location_indices, records_indices)]
    #lags = [x+1 for x in lagds]
    print(lags0)
    #records_grouped = df.groupby(by=records)
    team_records = []
    for _,team_df in df.groupby(by=team_location):
        # print(l)
        # print(team_df)
        # l = [-lag for lag in l if lag < 1]
        lags = range(0, len(team_df))
        #lags = team.index[]
        records_df = pd.DataFrame({f'{team_location}_{records}_{feature}-{n}':
                                  team_df[team_location + '_' + feature].shift(-n) for n in lags})
        print(records_df)
        team_record = pd.concat([team_df, records_df], axis=1)
        team_records.append(team_record)
    full_df = pd.concat(team_records, axis=0).sort_index()
    print(full_df)
    return full_df
    




test_df = pd.DataFrame({'date': ['25-may-2019', '25-may-2019', '1-june-2019',
                                     '1-june-2019', '8-june-2019', '8-june-2019',
                                     '15-june-2019', '15-june-2019', '22-june-2019',
                                     '29-june-2019', '29-june-2019', '6-july-2019'],
                            'h': ['A','C','B','D','A','B','C','D','D','A','B','C'],
                            'a': ['B','D','A','C','C','D','A','B','A','D','C','B'],
                            'h_ftgoals': [1,3,5,6,9,7,13,15,20,19,21,24],
                            'a_ftgoals': [0,4,2,6,8,10,12,16,20,18,22,24],
                            'result': ['hwin','awin','hwin','draw','hwin','awin',
                                       'hwin','awin','draw','hwin','awin','draw']})
print(test_df.head(15))
print('\n\n')
form_teams_records_(test_df)
