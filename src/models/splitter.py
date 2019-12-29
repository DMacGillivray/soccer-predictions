
class LeagueSeasonTimeSeriesFold():
    """
    Accepts a league season date sorted DataFrame containing a game_day column
    """
    def get_game_day_change_indices(self, X_df):
        return X_df['game_day'].diff()[X_df['game_day'].diff() != 0].index.values

    def split(self, X_df, y=None, groups=None):
        """
        Accepts a dataframe for a season with a 'game_day' column
        Splits into train, test for each game day in the season
        """
        game_day_indices = self.get_game_day_change_indices(X_df)
        for gd_index in game_day_indices[1:]:
            n_game_day = X_df.loc[gd_index]['game_day']
            train_indices = X_df[X_df['game_day'] < n_game_day].index
            test_indices = X_df[X_df['game_day'] == n_game_day].index
            yield train_indices, test_indices
