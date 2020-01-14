import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as ticker

from typing import List, Tuple, Union, Callable
from types import ModuleType

import pandas as pd
import numpy as np

from sklearn.calibration import calibration_curve
from netcal.metrics import ACE, ECE, MCE 


def extend_cols(additional_cols, include_target_cols=True):
    cols = ['nation', 'league', 'season', 'date', 'h', 'a']
    target_cols = ['h_ftGoals', 'a_ftGoals', 'h_shots', 'a_shots', 'h_shotsOnTarget', 'a_shotsOnTarget', 'result']
    if include_target_cols:
        cols.extend(target_cols)
    cols.extend(additional_cols)
    return cols


def vstacked_bar_charts(x: Union[pd.Series, pd.Index], ys: List[pd.Series],
                        figsize: Tuple[int, int]=(10,8)) -> Tuple[ModuleType, Tuple[ModuleType, ...]]:
    """
    TODO
    Checkout how to return matplotlib objects. Types are:
        class 'module'
        class 'matplotlib.axes._subplots.AxesSubplot'
    
    Accepts a pandas index specifying the x axis, and a list of pandas series specifying bar heights
    to be used on the different vertically stacked bar plots
    Returns the figure and the subplot axes
    """
    fig, axes = plt.subplots(ncols=1, nrows=len(ys),figsize=figsize, sharex=True)
    for ax,y in zip(axes, ys):
        ax.bar(x, y, alpha=0.5)
    return (fig, axes)

def diagnose_discrete_fit(x: Union[pd.RangeIndex, pd.Series],
                          obs: pd.Series,
                          fitted: pd.Series,
                         figsize=(14,14)) -> Tuple[ModuleType, Tuple[ModuleType, ...]]:
    obs = obs.values
    fitted = fitted.values
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=figsize)
    for i, ax in enumerate(fig.axes):
        if i == 0:
            ax.set_title('Histogram')
            
            ax.bar(x, obs)
            ax.plot(x, fitted, "ro-", lw=1)
            ax.vlines(x, 0, fitted, colors='b', lw=5, alpha=0.5)

        if i == 1:
            ax.set_title('Rootogram')
            
            obs = np.sqrt(obs)
            fitted = np.sqrt(fitted)
            ax.bar(x, obs)
            ax.plot(x, fitted, "ro-", lw=1)
            ax.vlines(x, 0, fitted, colors='b', lw=5, alpha=0.5)
        if i ==2:
            ax.set_title('Hanging Rootogram')
            
            ax.bar(x, obs)
            ax.plot(x, fitted, "ro-", lw=1)
            
            for fitted_val, rectangle in zip(fitted, ax.patches):
                y_min = 0
                diff = fitted_val - rectangle.get_height()
                if diff < y_min:
                    y_min = diff
                rectangle.set_y(diff)

                ax.plot(rectangle.get_x() + rectangle.get_width()/2.)
                ax.vlines(x, 0, fitted, colors='b', lw=5, alpha=0.5)
                
            # Get the lower limit of the y axis, but cannot be higher than 0 line
            y_ax_low = min([fitted_val - rectangle.get_height() for fitted_val, rectangle in zip(fitted, ax.patches)])
            if y_ax_low > 0:
                y_ax_low = 0
            ax.set_ylim(bottom=y_ax_low)
            # Put in a horizontal line along the x axis
            ax.axhline(0, lw=1, color='k')
            
        if i ==3:
            ax.set_title('Deviation Rootogram')
            
            ax.bar(x, obs)
            # Set the lower y axis limit to the value set in the previous (left hand) chart
            ax.set_ylim(bottom=y_ax_low)
            # Plot the expected points with a line
            ax.plot(x, fitted, "ro-", lw=1)
            # Put in a horizontal line along the x axis
            ax.axhline(0, lw=1, color='k')
            
            for fitted_val, rectangle in zip(fitted, ax.patches):
                y_min = 0
                diff = fitted_val - rectangle.get_height()
                if diff < y_min:
                    y_min = diff
                    rectangle.set_height(diff)
                    rectangle.set_y(0)
                if diff > y_min:
                    y_min = diff
                    rectangle.set_height(diff)
                    rectangle.set_y(0)
                ax.plot(rectangle.get_x() + rectangle.get_width()/2.)

    return (fig, fig.axes)


def plot_match_probas(home_probas: pd.Series, away_probas: pd.Series, goal_lim=6, figsize=(12,12)):
    """
    
    """
    # https://stackoverflow.com/questions/37008112/matplotlib-plotting-histogram-plot-just-above-scatter-plot
    # https://stackoverflow.com/questions/4018860/text-box-with-line-wrapping-in-matplotlib
    # Note text wrapping not working See here
    # https://stackoverflow.com/questions/48079364/wrapping-text-not-working-in-matplotlib
    # Collect probabilities for scores > goal limit into the last goal bucket
    if goal_lim < len(home_probas):
        home_probas.iloc[goal_lim] = home_probas[goal_lim:].sum()
        home_probas = home_probas.iloc[:goal_lim+1]
    if goal_lim < len(away_probas):
        away_probas.iloc[goal_lim] = away_probas[goal_lim:].sum()
        away_probas = away_probas.iloc[:goal_lim+1]
        
    # Form the probability Matrix    
    mat = np.multiply(home_probas.values.reshape(1,len(home_probas)),
                                                 away_probas.values.reshape(len(away_probas),1))
    mat = np.round(mat,2)
    
    # Get the probabilities from the array using triangles
    phwin = np.round(np.sum(np.triu(mat, k=1)),4)
    pawin = np.round(np.sum(np.tril(mat, k=-1)),4)
    pdraw = np.round(np.sum(np.diag(mat)),4)
    
    
    # Set up the plot
    fig = plt.figure(figsize=figsize)
    gs = GridSpec(4,4)
    ax_joint = fig.add_subplot(gs[1:4,0:3])
    ax_marg_x = fig.add_subplot(gs[0,0:3])
    ax_marg_y = fig.add_subplot(gs[1:4,3])
    ax_box = fig.add_subplot(gs[0:1,3:4])
    ax_box.axis('off')

    # Box Text
    ax_box.text(0.0, 0.0,
                f"""Home: {home_probas.name}\n
                Away:{away_probas.name}\n
                \n
                Probabilities:\n
                Home Win: {phwin}\n
                Draw:         {pdraw}\n
                Away Win: {pawin}
                """,
                ha='left',
               wrap=True)


    ax_joint.imshow(mat, cmap='Blues', interpolation='nearest')
    ax_marg_x.bar(home_probas.index, home_probas)
    ax_marg_y.barh(away_probas.index, away_probas, orientation="horizontal")

    ax_marg_x.set_xlabel(f'{home_probas.name}')
    ax_marg_y.set_ylabel(f'{away_probas.name}')

    # Place values into heatmap boxes
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            text = ax_joint.text(j, i, mat[i, j],
                           ha="center", va="center", color="r")

    # Set labels on joint
    ax_joint.set_xlabel('Home Goals')
    ax_joint.set_ylabel('Away Goals')

    # Set values on distribution heights
    all_probs = np.concatenate((home_probas, away_probas))
    pmin = np.min(all_probs)
    pmax = np.max(all_probs)+0.05
    
    loc = ticker.MultipleLocator(base=0.05) # this locator puts ticks at regular intervals
    ax_marg_x.yaxis.set_major_locator(loc)
    ax_marg_y.xaxis.set_major_locator(loc)

    ax_marg_x.set_ylim(pmin, pmax)
    ax_marg_y.set_xlim(pmin, pmax)

    ax_marg_y.invert_yaxis()

    # Set labels on marginals
    ax_marg_y.set_xlabel('Probability')
    ax_marg_x.set_ylabel('Probability')
    plt.tight_layout()
    return fig, (fig.axes) 


def get_model_diagnosis(df, strategy='quantile', rps_col_prefix='model', add_baseline=False):
    """
    Diagnosis Plots:
    Accepts a DataFrame containing columns:
    ordinal_result_1
    ordinsl_result_2
    ordinal_result_3
    1
    2
    3
    The columns are paired as follows:
    "ordinal_result_1" represents a binary column defining
    whether a home win event occurred, and
    column named "1" contains the corresponding model probabilities
    Same for ordinal_result_2, and 2 and
    ordinal_result_3 and 3
    strategy{‘uniform’, ‘quantile’}, (default=’uniform’)
    Strategy used to define the widths of the bins.
      uniform
        All bins have identical widths.
      quantile
        All bins have the same number of points.
    RPS Plots:
    Accepts a DataFrame containing columns:
    ordinal_result
    "rps_col_prefix"_rps
    and optional columns named
    rps_baseline_1
    2
    3
    The columns are paired as follows:
    "ordinal_result_1" represents a binary column defining
    whether a home win event occurred, and
    column named "1" contains the corresponding model probabilities
    Same for ordinal_result_2, and 2 and
    ordinal_result_3 and 3
    """
    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(12,10))
    ax1, ax2, ax3 = axes[:, 0]
    n_bins = 10
    mapper = {1: 'Home Win', 2: 'Draw', 3: 'Away Win'}
    for col, ax in zip([1,2,3], (ax1, ax2, ax3)):
        fop, mpv = calibration_curve(df['ordinal_result_' + str(col)],
                                     df[col],
                                     n_bins=n_bins,
                                     strategy=strategy)
        # plot perfectly calibrated
        ax.plot([0, 1], [0, 1], linestyle='--')
        # plot model reliability
        ax.plot(mpv, fop, marker='.')
        ax.set_title(mapper[col])

    ax4, ax5, ax6 = axes[:, 1]
    n_bins = 10
    mapper = {1: 'Home Win RPS', 2: 'Draw RPS', 3: 'Away Win RPS'}
    for col, ax in zip([1, 2, 3], (ax4, ax5, ax6)):
        rpss = df[df['ordinal_result'] == col][rps_col_prefix + '_rps']
        ax.hist(rpss, bins=n_bins)
        ax.set_xlim(0, 1.0)
        baseline_col_name = 'rps_baseline_' + str(col)
        if add_baseline and baseline_col_name in df.columns:
            ax.axvline(df['rps_baseline_1'].unique(), color='r')
        median = rpss.median()
        ax.axvline(median, color='r', linestyle='dashed', label=f'Median: {median:.3f}')
        ax.set_title(mapper[col])
        ax.legend()
        ax.grid()

    pred_arr, act_arr = df[[1, 2, 3]].values, df['ordinal_result'].values

    ace = ACE(bins=n_bins)
    ace_val = ace.measure(pred_arr, act_arr)

    ece = ECE(bins=n_bins)
    ece_val = ece.measure(pred_arr, act_arr)

    mce = MCE(bins=n_bins)
    mce_val = mce.measure(pred_arr, act_arr)

    print(f'Average Calibration Error:  {ace_val:.3f}\nExpected Calibration Error: {ece_val:.3f}\nMaximum Calibration Error:  {mce_val:.3f}')
    print(f"Number of Instances: {len(df)}")
    return fig, (ax1, ax2, ax3, ax4, ax5, ax6)
