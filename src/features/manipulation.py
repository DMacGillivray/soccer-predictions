
def cut_historical_games(df_orig, n_back, drop_all_nan_rows=True, how='all'):
    df = df_orig.copy(deep=True)
    feature_cols = [col for col in df.columns if '-' in col]
    non_feature_cols = [col for col in df.columns if col not in feature_cols]
    cut_feature_cols = [col for col in feature_cols
                        if int(col.rsplit('-')[1]) <= n_back]
    return_cols = non_feature_cols + cut_feature_cols
    df = df[return_cols]
    if drop_all_nan_rows:
        df.dropna(subset=cut_feature_cols, axis=0, inplace=True, how=how)
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


def get_feature_name_stubs(df, feature_names):
    return list(set([col.rsplit('-', 1)[0] for col in df.columns
                     if 'ftGoals' in col and '-' in col]))


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
