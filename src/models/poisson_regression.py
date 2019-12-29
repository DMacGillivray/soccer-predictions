from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_is_fitted
from sklearn.utils.multiclass import unique_labels

import pandas as pd
import numpy as np
from scipy.stats import poisson
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.tools.sm_exceptions as sm_exceptions


class PoissonRegression(BaseEstimator, ClassifierMixin):
    """
    Adapted from:
    https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling/
    fit accepts a DataFrame representing an early part of a league season
    Reshapes the data, and fits a Regression Model based on this data
    predict / predict_proba accepts a dataFrame representing a later,
    consecutive part of a league season.
    Reshapes the data and makes, and returns
    home win, draw, and away win probabilities

    DataFrame must have the following data columns
    h - home team, a - away team
    h_ftGoals - home team full time goals
    a_ftGoals - away team full time goals
    """
    def __init__(self, family=sm.families.Poisson(),
                 formula='goals ~ home + team + opponent',
                 max_goals=10):
        self.family = family
        self.formula = formula
        self.max_goals = max_goals
        self.epsilon = 0.1
        self.model = None

    def fit(self, X, y):
        """
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The training input samples.
        y : Not used
        Returns
        -------
        self : object
            Returns self.
        """
        # Store the classes seen during fit
        self.classes_ = unique_labels(y)
        self.X_ = X
        self.y_ = y

        # Reshape the data
        self.reshaped_X_ = pd.concat([self.X_[['h', 'a', 'h_ftGoals']].assign(home=1).rename(
                             columns={'h': 'team', 'a': 'opponent', 'h_ftGoals': 'goals'}),
                             self.X_[['a', 'h', 'a_ftGoals']].assign(home=0).rename(
                             columns={'a': 'team', 'h': 'opponent', 'a_ftGoals': 'goals'})])

        # fit the model - have to handle perfect separation or not enough data
        # If exception - catch and the the model to None
        # If we see  None model in predict, we can return 0 probabilities
        # to show that the model did not do the prediction
        try:
            self.model = smf.glm(formula=self.formula,
                                 data=self.reshaped_X_,
                                 family=self.family).fit()
        except sm_exceptions.PerfectSeparationError:
            # print('sm_exceptions.PerfectSeparationError')
            self.model = None
        except ValueError:
            # print('ValueError')
            self.model = None
        # Return the classifier
        return self.model

    def calc_probas(self, row):
        team_pred = [[poisson.pmf(i, team_avg) for i in range(0, self.max_goals+1)]
                     for team_avg in [row['h_lambda'], row['a_lambda']]]
        prob_table = np.outer(np.array(team_pred[0]), np.array(team_pred[1]))
        phwin = np.sum(np.tril(prob_table, -1))
        pdraw = np.sum(np.diag(prob_table))
        pawin = np.sum(np.triu(prob_table, 1))
        # Return in same sequence as classes_
        return phwin, pdraw, pawin

    def predict(self, X):
        """ A reference implementation of a prediction for a classifier.
        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            The input samples.
        Returns
        -------
        y : ndarray, shape (n_samples,)
            The label for each sample is the label of the closest sample
            seen during fit.
        """
        # Check is fit had been called
        check_is_fitted(self, ['X_', 'y_'])

        if self.model is not None:
            # Reshape the data and make the poisson predictions
            h_preds = self.model.predict(pd.DataFrame(data={'team': X['h'].values,
                                                      'opponent': X['a'].values,
                                                            'home': 1}))
            a_preds = self.model.predict(pd.DataFrame(data={'team': X['a'].values,
                                                      'opponent': X['h'].values,
                                                            'home': 0}))
            temp_df = pd.DataFrame({'h_lambda': h_preds, 'a_lambda': a_preds})
            self.probas = temp_df.apply(self.calc_probas, axis=1, result_type='expand')
            self.probas.columns = ['poiss_p(hwin)', 'poiss_p(draw)', 'poiss_p(awin)']
        else:
            self.probas = pd.DataFrame({'poiss_p(hwin)': [np.NaN]*len(X),
                                        'poiss_p(draw)': [np.NaN]*len(X),
                                        'poiss_p(awin)': [np.NaN]*len(X)})

        # When there is not enough data to predict, the model can
        # create some non-sensical probabilities
        # Clean these up by setting all 3 probabilities to 0
        crit1 = self.probas.sum(axis=1) < 1.0 - self.epsilon
        crit2 = self.probas.sum(axis=1) > 1.0 + self.epsilon
        self.probas[crit1 | crit2] = np.NaN

        # Set the index of the returned probabilities to match the input data
        self.probas.index = X.index

        return self.probas.idxmax(axis=1)

    def predict_proba(self, X):
        self.predict(X)
        rename_dict = {'poiss_p(hwin)': 'h_poissWin',
                       'poiss_p(draw)': 'h_poissDraw',
                       'poiss_p(awin)': 'h_poissLose'}
        self.probas.rename(columns=rename_dict, inplace=True)
        self.probas['a_poissDraw'] = self.probas['h_poissDraw']
        self.probas['a_poissWin'] = self.probas['h_poissLose']
        self.probas['a_poissLose'] = self.probas['h_poissWin']

        return self.probas
