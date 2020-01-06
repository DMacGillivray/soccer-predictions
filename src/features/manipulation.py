
def cut_historical_games(df_orig, n_back, drop_all_nan_rows=True, how='all'):
    df = df_orig.copy(deep=True)
    feature_cols = [col for col in df.columns if '-' in col]
    non_feature_cols = [col for col in df.columns if col not in feature_cols]
    pre_game_feature_cols = [col for col in df.columns
                             if '-' in col and
                             ('poiss' in col or 'implied' in col)]
    cut_pre_game_feature_cols = [col for col in pre_game_feature_cols
                                 if int(col.rsplit('-')[1]) <= n_back]
    sub_feature_cols = [col for col in feature_cols
                        if 'poiss' not in col or 'implied' not in col]
    cut_feature_cols = [col for col in sub_feature_cols
                        if int(col.rsplit('-')[1]) <= n_back
                        and int(col.rsplit('-')[1]) > 0]
    return_cols = non_feature_cols + cut_pre_game_feature_cols\
        + cut_feature_cols
    df = df[return_cols]
    if drop_all_nan_rows:
        df.dropna(subset=cut_feature_cols, axis=0, inplace=True, how=how)
    df = df.loc[:, ~df.columns.duplicated()]
    df.reset_index(drop=True, inplace=True)
    return df


def select_features(df_orig, feature_name_stubs):
    df = df_orig.copy(deep=True)
    all_feature_cols = [col for col in df.columns if '-' in col]
    other_cols = [col for col in df.columns if col not in all_feature_cols]
    ret_feature_cols = []
    for feature_name_stub in feature_name_stubs:
        feature_cols = [col for col in df.columns if col in all_feature_cols]
        ret_feature_cols.extend(feature_cols)

    return_cols = other_cols + ret_feature_cols
    return df[return_cols]


def get_feature_name_stubs_from_base(df, feature_names):
    feature_name_stubs = []
    for feature_name in feature_names:
        feature_name_stubs.extend(list(set([col.rsplit('-', 1)[0] for col
                                            in df.columns
                                            if feature_name ==
                                            col.rsplit('-', 1)[0][4:]
                                            and '-' in col])))
    return feature_name_stubs


def get_base_features(df):
    return sorted(list(set([col.rsplit('-', 1)[0][4:]
                            for col in df.columns if '-' in col])))


def get_df_from_base_features(df_orig, base_features):
    df = df_orig.copy(deep=True)
    all_feature_cols = [col for col in df.columns if '-' in col]
    other_cols = [col for col in df.columns if col not in all_feature_cols]
    feature_col_sets = []
    for base_feature in base_features:
        feature_col_set = [col for col in all_feature_cols
                           if base_feature in col]
        feature_col_set.sort(key=lambda x: int(x.rsplit('-', 1)[1]))
        feature_col_sets.extend(feature_col_set)
    ret_cols = other_cols + feature_col_sets
    return df[ret_cols]


def get_features_df(df_orig):
    df = df_orig.copy(deep=True)
    feature_cols = [col for col in df.columns if '-' in col]
    return df[feature_cols]


def get_non_features_df(df_orig):
    df = df_orig.copy(deep=True)
    non_feature_cols = [col for col in df.columns if '-' not in col]
    return df[non_feature_cols]


def get_target_df(df_orig, format='single_ordinal_result_column'):
    df = df_orig.copy(deep=True)
    if format == 'single_ordinal_result_column':
        return df['ordinal_result']
    if format == 'ordinal_result_columns':
        return df[['ordinal_result_1', 'ordinal_result_2', 'ordinal_result_3']]
