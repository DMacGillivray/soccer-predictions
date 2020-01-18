
# Soccer Predictions

1. [Business Opportunity: Odds Advice](#1-business-opportunity-odds-advice)
2. [Data Source Review](#2-data-source-review)
3. [Data Wrangling](#3-data-wrangling)
4. [Exploratory Data Analysis](#4-exploratory-data-analysis)
5. [Modeling Strategy](#5-modeling-strategy)
6. [Feature Engineering](#6-feature-engineering)
7. [Feature Selection](#7-feature-selection)
8. [Modeling](#8-modeling)
9. [Model Prediction and Review](#9-model-prediction-and-review)
10. [Selecting the Best Model](#10-selecting-the best-model)
11. [Test Data Results](#11-test-data-results)
12. [Next Steps](#12-next-steps)
13. [Conclusion](#13-conclusion)
14. [Tips for Reproducing This Project](#14-tips-for-reproducing-this-project)
<br/><br/>

## 1. Business Opportunity: Odds Advice

### 1.1 Customer

As more states [legalize sports betting](https://www.marketwatch.com/story/in-2020-we-will-see-how-widespread-legalized-sports-betting-becomes-2019-12-18), the opportunities to provide bettor services grows.

The business proposal is a web service that enables a bettor to identify profitable bets on European soccer games

### 1.2 Service Description


The scope will be for 3 of the top European Leagues

+ English Premier League - 20 teams playing 380 games per season
+ German Bundesliga - 18 teams playing 306 games per season
+ Italian Serie A - 20 teams playing 380 games per season

Each league season is structured the same way. Every team plays every other team at home and away, and each game has one of four outcomes:

+ Home Team Wins
+ Draw
+ Away Team Wins
+ Game Abandoned (or some other unique event occurs) - This is so rare that it will be neglected in this analysis

The web service will provide a list of upcoming games, along with the minimum odds required to make a profitable bet.

So, if for example, on Saturday, there are 20 games being played across these 3 leagues, 60 minimum odds recommendations will be made - 3 for each game - An example is shown below:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/web-service-profitable-odds-table.png" width="807" height="136" />
</p>

### 1.3 Customer Value

The bettor will take these numbers and scan the Sports Books for odds higher than these. For the service to be good, it needs to consistently find the minimum odds needed to enable a bettor to make profitable bets over the long run. Note that it may not always possible to find profitable odds at the Sports Books.

So if I want to bet on Liverpool winning their 21 January game against Manchester United, I would find a Sports Book giving decimal odds higher than 1.5, and place the bet.

### 1.4 Business Objective

Identify break-even odds for the next set of soccer games to be played in the Premier League, Bundesliga, and Serie A

#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 

## 2. Data Science Objective

Develop a model based on free & publicly available data that will identify break-even odds for the next set of soccer games to be played in the Premier League, Bundesliga, and Serie A

## 3. Understanding the Data Science Objective

### 3.1 Randomness in Soccer Games

There is a significant degree of [randomness involved in soccer games](https://www.nytimes.com/2014/07/08/science/soccer-a-beautiful-game-of-chance.html). We can never really know with 100% confidence what the final score will be. This is very different to a standard classification problem - say classifying images of cats and dogs. For cats and dogs there is a solid ground truth for the class. A cat is a cat with 100% certainty. A random outcome, like a Soccer game result is different; We can never get to the point where we are predicting a single outcome with 100% certainty, because the outcome itself is uncertain.

I propose that if we do a thought experiment and imagine that a football game between the same 2 teams was played 100 times, we could reasonably assume that we would not get the same final score for all 100 games. In fact it could be argued that the inherent randomness in the game is what makes it so exciting, and hence so popular.

Because of the probabilistic nature of the outcome, we need to carefully consider the types of models we use to classify game outcomes. **Our objective is not accurate classification, but accurate probabilities.**

### 3.2 What Makes a Profitable Bet?

We can think of a football game like this. If the same game were played a million times, how would the possible outcomes be proportioned?

Let us assume we simulated 1,000,000 games, and imagine the home team won 320,000 times, there was a draw 270,000 times, and the away team won 410,000 times

With this (imaginary) data we would be able to say the probability distribution for the game results would be as follows:

Home Win                 |	Draw     | Away Win
:------------------------:|:--------------:|:------------:
0.32                   |	0.27    | 0.41

The next component to the bet is the odds.

If we go to 2 Sports Books and find the following odds for home wins – How do we know which bets are profitable?

Odds # 1                 |	Odds # 2
:------------------------:|:--------------:
2.92                   |	3.30


 
We can calculate the Expected Value of the bet, to see which odds are favourable

Expected Value (EV) is the probability of winning the bet multiplied by the potential winnings minus the probability of losing the bet multiplied by our potential loss.

In the following calculations we will call the amount we will place on the bet the stake, and assume it equals 1 unit. We now have all the elements needed to make an Expected Value calculation.

+ probability of winning: 0.32
+ probability of losing: 1 - probability of winning, or 1 - 0.32 = 0.68
+ potential winnings: odds - stake, or odds - 1 when stake = 1
+ potential loss: stake, or 1

<a href="https://www.codecogs.com/eqnedit.php?latex=EV&space;=&space;(probability\;of\;winning\;bet&space;\times&space;(odds&space;-&space;stake)))&space;-&space;(probability\;of\;losing\;bet&space;\times&space;-&space;stake))" target="_blank"><img src="https://latex.codecogs.com/gif.latex?EV&space;=&space;(probability\;of\;winning\;bet&space;\times&space;(odds&space;-&space;stake)))&space;-&space;(probability\;of\;losing\;bet&space;\times&space;-&space;stake))" title="EV = (probability\;of\;winning\;bet \times (odds - stake))) - (probability\;of\;losing\;bet \times - stake))" /></a>

If we apply this formula to our different odds, and use a unit stake, we get:

+ Odds # 1:

 <a href="https://www.codecogs.com/eqnedit.php?latex=EV&space;=&space;(0.32&space;\times&space;(2.92\;&space;-\;&space;1))\;&space;&plus;\;&space;((1-0.32)&space;\times&space;-&space;1)&space;=&space;-0.0656" target="_blank"><img src="https://latex.codecogs.com/gif.latex?EV&space;=&space;(0.32&space;\times&space;(2.92\;&space;-\;&space;1))\;&space;&plus;\;&space;((1-0.32)&space;\times&space;-&space;1)&space;=&space;-0.0656" title="EV = (0.32 \times (2.92\; -\; 1))\; +\; ((1-0.32) \times - 1) = -0.0656" /></a>
+ Odds # 2:

 <a href="https://www.codecogs.com/eqnedit.php?latex=EV&space;=&space;(0.32&space;\times&space;(3.30\;&space;-\;&space;1))\;&space;&plus;\;&space;((1-0.32)&space;\times&space;-&space;1)&space;=&space;0.056" target="_blank"><img src="https://latex.codecogs.com/gif.latex?EV&space;=&space;(0.32&space;\times&space;(3.30\;&space;-\;&space;1))\;&space;&plus;\;&space;((1-0.32)&space;\times&space;-&space;1)&space;=&space;0.056" title="EV = (0.32 \times (3.30\; -\; 1))\; +\; ((1-0.32) \times - 1) = +0.056" /></a>

So, If we can get Odds #2, we have a positive EV bet, and if we trust our probability prediction, we should place the bet. Alternatively, if we can only get Odds #1, we have a negative EV, and we should avoid the bet.

Clearly, even with positive EV, we may lose this particular bet. In fact, we recognize we have only a 32% probability of winning the bet, which means we have a much higher - 68% - probability of losing the bet. However, over the long run, if we are correctly identifying, and placing, positive EV bets, we will make money.

The counter-intuitive implication of using EV, is that if we find 2 positive EV bets on the same game - say Home Win, and Draw, then in theory we should place both bets! We will deal with this issue later.



### 3.3 Implied Probability and the Overround

The Sports Book will produces a set of odds for a game that looks like this:

Home Win                 |	Draw     | Away Win
:------------------------:|:--------------:|:------------:
2.92                   |	3.52    | 2.3

These odds can be converted to "probabilities" - We just need to divide the odds into 1.

Home Win                 |	Draw     | Away Win
:------------------------:|:--------------:|:------------:
2.92                   |	3.52    | 2.3
0.342                   |	0.284    | 0.435

However, looking at these numbers, it is clear that they are not real probabilities. The problem is when we add them together, they sum to 1.061. We know that these 3 outcomes are the only possible outcomes, so "real" probabilities should sum to exactly 1. What explains this discrepancy?

This is where the Sports Book makes money, and is known as the [overround or the "vig"](https://en.wikipedia.org/wiki/Mathematics_of_bookmaking#Making_a_'book'_(and_the_notion_of_overround))

However, we can normalize these 3 numbers back to implied probabilities by dividing by the sum

The table below shows Expected Value calculations on some typical odds 

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/odds-to-EV-calculation-table.png" width="599" height="317" />
</p>



## 4. Data Sources and Description


### 4.1 www.football-data-co-uk

This site contains a vast amount of archived data for multiple football leagues. Crucially, it also contains Odds Data

Typical Data

+ Nation, League, Season
+ Date, Home Team, Away Team
+ Full Time Home Team Goals, Full Time Away Team Goals
+ For each team:
	+ Corners
	+ Fouls
	+ Red Cards
	+ Yellow Cards
	+ Shots
	+ Shots on Target
	+ other data dependent on recency and particular league
+ Home Win Odds, Draw Odds, Away Win Odds:
	+ by Sports Book for 5 or 6 Sports Books
	+ Maximum Odds
	+ Mean Odds
	+ Other Odds such as Asian, and Goal Difference Odds
	
### 4.2 www.indatabet.com (Site no longer available)

An Odds data site with a massive archive of odds across multiple competitions

Typical Data

+ Nation, League, season
+ Date, Home Team, Away Team
+ Full Time Goals
+ Home Win Odds, Draw Odds, Away Win Odds:
	+ for Pinnacle, Bet365 Sports Books


## 5. Exploratory Data Analysis

### 6.1 Match Results

Taking data for the German Bundesliga for all games from the 2007-2008 season up to the 2014-2015 season, we can see that there is a [home-field advantage)(https://en.wikipedia.org/wiki/Home_advantage), in that about 45% of games are won by the home team

As shown 

Home Win                 |	Draw     | Away Win
:------------------------:|:--------------:|:------------:
0.455                   |	0.246    | 0.297

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-proportion-of-results-barplot.PNG" width="720" height="504" />
</p>


eda-proportion-of-results-scatterplot

This effect is consistent from season to season as shown below

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-proportion-of-results-scatterplot.PNG" width="720" height="504" />
</p>



### 6.2 Goals

The home-field advantage shows up in goals scored, as shown below:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-multiple-seasons-home-and-away-goals-barplots.PNG" width="1008" height="576" />
</p>

Reviewing the chart above, we can see that the mean and variance are roughly equal for the count distributions. this point us in the direction of considering goals scored as a poisson distribution.


If we fit a poisson distribution to the data, we can use some diagnosis plots to compare the theoretical to the actual distribution. This is shown below for goals scored by the home team, and it looks like a remarkably good fit.
<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-home-goals-poisson-fit-diagnosisplots.PNG" width="1008" height="1008" />
</p>




### 6.3 Odds

Reviewing the odds data, we can see that the odds of a Home Win, and a Draw have a much lower maximum than the odds for an Away Win. The Away Win odds scale is much larger. This makes sense when we consider that the reciprocal of the odds can be interpreted as being close to a probability. If the probability of an Away Win is much less likely, then the odds increase.

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-odds-bundesliga-multipl-bookies-multiple-seasons-histograms.PNG" width="864" height="576" />
</p>

TODO: redo with same shared x scale

### 6.4 Shots

### 6.5 Shots on Target

### 6.6 Other Match Data

### 6.7 Expected Goals xG

### 6.8 League Differences

#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 


## 7. Features

Across season features neglected

### 7.1 Model Results as Features

### 7.2 Poisson Regression

### 7.3 Odds as Implied Probabilities

### 7.4 Game Data

## 8. Data Work Flow

## 9. Metrics and model Diagnosis

Note on probability Calibration

### 9.1 Reliability Diagrams and Multi-Class calibration Metrics

calibration is an assessment of the goodness of the probability estimates from a model.

Consider that we could select all instances where a model has predicted an 80% probability of an event.

We can then look at the frequency of occurrence of the event across those instances

If the event actually occurs about 80% of the time, then our model is well calibrated.

If the event actually occurs about 20% of the time, then our model is over-confident.

If the event actually occurs over 99% of the time, then our model is under-estimating the true probability.

Perfect calibration looks like this:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/perfect-calibration-plot.png" width="372" height="266" />
</p>

*The above plot is taken from [Alon Daks web site](http://alondaks.com/me/) from the article[The Importance of Calibrating Your Deep Production Model](http://alondaks.com/2017/12/31/the-importance-of-calibrating-your-deep-model/)*


#### 9.2 Expected Calibration Error


<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/ECE-formula.png" width="559" height="108" />
</p>
See [The Importance of Calibrating Your Deep Production Model](http://alondaks.com/2017/12/31/the-importance-of-calibrating-your-deep-model/) for details

#### Maximum Calibration Error 

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/MCE-formula.png" width="581" height="75" />
</p>

See [The Importance of Calibrating Your Deep Production Model](http://alondaks.com/2017/12/31/the-importance-of-calibrating-your-deep-model/) for details


### 9.2 Rank probability Score

The objective of the project is to identify profitable betting opportunities. A profitable betting opportunity is captured if we are good at estimating its’ Expected Value. Expected Value is determined by 2 inputs:
    • The probabilities output by the model
    • The odds given by the bookmaker
We have to remember that our model is producing probabilities of an event, but the event is itself somewhat random.
We cannot control the odds given by the bookmaker, but we can try and develop a model that is “good” at predicting the outcome probabilities. Note that this is different to accurately classifying outcomes. How do we assess the probability output from the model?
One [possible](https://arxiv.org/pdf/1908.08980.pdf) answer lies in a 2011 paper [“Solving the problem of inadequate scoring rules for assessing probabilistic football forecast models”](https://www.semanticscholar.org/paper/Solving-the-Problem-of-Inadequate-Scoring-Rules-for-Constantinou-Fenton/90a56f63a08784f3f63e853c30bedea48df4e478) This paper shows that soccer results can be thought of as an ordinal ranking. Home win is first, followed by a draw, followed by an away win, and that tool called the  Rank Probability Score is a better way to assess predictions.

What is the Rank Probability Score?
This measures how good a probability forecast is at classifying an observed outcome. A perfect score is 0, the worst possible score is 1
Formula goes here
Consider Extreme Predictions, and the impact on RPS
It is worthwhile reviewing some examples of Rank Probability Scores for the 3 possible match outcomes – home win, draw, and away win



<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/rps-extreme-examples.png" width="724" height="429" />
</p>

This table is enlightening. It is comprised of extreme prediction probabilities where we predict an outcome with absolute certainty – Our forecast probabilities are either 0 or 1
    • For RPS a lower score is better
    • We score an RPS of 0, when we predict an outcome with a probability of 1
    • The best possible RPS for all outcomes – home win, draw, away win is 0
    • The worst possible RPS for an observed Home or Away Win is 1.0
    • The worst possible RPS for an observed Draw is 0.5 – this is the impact of a draw being the middle of the 3 outcomes
    
 Consider Baseline Frequency Predictions, and the impact on RPS
European soccer has a significant home field advantage. This varies over time, but a home win is far more likely than either a draw, or an away win. In fact a home win is about twice as likely.
We can plug some rough baseline frequencies into our RPS calculation and determine and review the results. 


<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/rps-baseline-values-table.png" width="724" height="181" />
</p>

Some comments on this table:

+ The RPS for each baseline frequency is different depending on the actual outcome
+ There is a significant difference between the best (lowest) Draw, and the highest (worst) Away Win
+ This means that just using baseline frequency predictions, we do far better at predicting draws, than we do at predicting either home Wins, or away Wins.

### 9.3 Probability Calibration


### 9.5 Model Diagnosis Suite

It seems there is no single number that will conveniently allow us to make a comparison between various models.

Therefore, I propose a Diagnosis Suite as follows:

+ Values for Calibration of Multi-class Results 		+ Expected Calibration Error
	+ Maximum calibration Error
+ Calibration Plots for each Class
+ RPS Distribution Plots for each Predicted Class

A sample Diagnosis suite is shown below:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/model-diagniosis-suite.png" width="731" height="668" />
</p>
 
 Explanation of how to interpret



#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 

## 10. Modeling

### 10.1 Dealing with Class Imbalance

### 10.2 Feature Compression

### 10.3 Feature Selection

### 10.4 Model Comparison on Validation Data

### 10.5 Model Performance on Held out Test Data

#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 

##11. Business Results

#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 

## 12. Next Steps

## Apendix A: Software Packages

Package                 |	Version     | Usage
:------------------------|:--------------:|:------------
Python                   |	3.7.3    | Code
Jupyter Notebook Client  |	5.3.1 | Code Organization
Matplotlib	| 3.1.1  | Visualization
Seaborn	| 0.9.0  | Visualization
Pandas	| 0.25.1  | Data Manipulation
Scikit Learn	| 0.20.0  | Machine Learning
XGBoost	| 0.90  | Machine Learning
Statsmodels	| 0.10.1  | Analysis including ARIMA Models
FbProphet	| 0.5  | Bayesian Time Series Modelling
Pymc3	| 3.7  | Bayesian Modelling
Pdarima	| 1.2.0  | Automatic Parameter Finding for ARIMA Models
Skoot	| 0.20.0  | Machine Learning Transformations on Pandas DataFrames
Skyfield	| 1.11  | Solstice Calculations
Holidays    | 0.9.11   | Statutory Vacation Days


## Appendix B: Summary of Data Sources

+ Electricity Demand
	* Data used in this project - Ontario Hourly Electrical Demand 1994 to 2019 [Data Directory](https://github.com/DMacGillivray/ontario-peak-power-forecasting/tree/master/data/01-raw/demand)
+ Electricity Demand Data Sources & Resources
	+ [Independent Electricity System Operator (IESO) Web Page  - Data Directory](http://www.ieso.ca/Power-Data/Data-Directory)
	+ [Download - Ontario Electricity Demand 1994 - 2002](http://www.ieso.ca/-/media/Files/IESO/Power-Data/data-directory/HourlyDemands_1994-2002.csv?la=en)
	+ [Download - Ontario Electricity Demand 2002 to present](http://reports.ieso.ca/public/Demand/)

+ Weather
	* Data used in this project - Toronto (YYZ) Hourly Weather 1953 to 2019 - [Data Directory](https://github.com/DMacGillivray/ontario-peak-power-forecasting/tree/master/data/01-raw/weather-toronto)
+ Weather Data Sources & Resources
	* [Historical Weather Data Search Page](https://climate.weather.gc.ca/historical_data/search_historic_data_e.html)
	* [How to use - Historical Data pdf](https://climate.weather.gc.ca/doc/Historical_Data_How_to_Use.pdf)
	* [How to bulk download historical weather data from Canadian government website using R](https://stackoverflow.com/questions/53824071/how-to-bulk-download-historical-weather-data-from-canadian-government-website-us/53939602#53939602)
	* [Download Scripts for Canadian Weather Bulk Download](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/src/raw-data/wget-bulk-weather.txt)


<br/><br/>


						David MacGillivray – Springboard Capstone Project 1 – 9 October 2019


<br/><br/>

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>

