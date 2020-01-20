
# Soccer Predictions

1. [Business Opportunity: Odds Advice](#1-business-opportunity-odds-advice)
2. [Data Science Objective](#2-data-science-objective)
3. [Understanding the Business Objective](#3-understanding-the-business-objective)
4. [Data Sources and Description](#4-data-sources-and-description)
5. [Exploratory Data Analysis](#5-exploratory-data-analysis)
6. [Metrics and Model Diagnostics](#6-metrics-and-model-diagnostics)
7. [Data Wrangling](#7-data-wrangling)
8. [Features and Feature Engineering](#8-features-and-feature-engineering)
9. [Modeling](#9-modeling)
10. [Model Results](#10-model-results)
11. [Business Results](#11-business-results)
12. [Conclusion](#12-conclusion)
13. [Next Steps](#13-next-steps)
14. [Software Packages](#14-software-packages)
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


## 2. Data Science Objective

Develop a model based on free & publicly available data that will identify break-even odds for the next set of soccer games to be played in the Premier League, Bundesliga, and Serie A

## 3. Understanding the Business Objective

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

#### Notebooks
+ [Business Objective - Betting, Expected Values](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/003.001%20Business%20Objective-%20Betting%2C%20Expected%20Values.ipynb) 


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

#### Notebooks
+ [Data Sources - www.football-data.co.uk](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/004.001%20-%20Data%20Sources%20-%20www.football-data.co.uk.ipynb) 

+ [Data Sources - www.indatabet.com](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/004.002%20-%20Data%20Sources%20-%20www.indatabet.com.ipynb)


## 5. Exploratory Data Analysis

### 5.1 Match Results

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



### 5.2 Goals

The home-field advantage shows up in goals scored, as shown below:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-multiple-seasons-home-and-away-goals-barplots.PNG" width="1008" height="576" />
</p>

Reviewing the chart above, we can see that the mean and variance are roughly equal for the count distributions. this point us in the direction of considering goals scored as a poisson distribution.




If we fit a poisson distribution to the data, we can use some diagnosis plots to compare the theoretical to the actual distribution. This is shown below for goals scored by the home team, and it looks like a remarkably good fit.
<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-home-goals-poisson-fit-diagnosisplots.PNG" width="1008" height="1008" />
</p>

Note: Research has shown that the [Home Field Advantage varies from league to league](https://dashee87.github.io/data%20science/python/home-advantage-in-football-leagues-around-the-world/). The European leagues seem similar, but based on watching soccer, I am not convinced they are the same. Therefore, I propose training a separate model for each league. I suspect that the same type of model (e.g. decision tree) may work best across multiple leagues, but I think the fitted parameters could be different. I base this suspicion on my intuition that the style of soccer played in each league is different.


### 5.3 Odds

Reviewing the odds data, we can see that the odds of a Home Win, and a Draw have a much lower maximum than the odds for an Away Win. The Away Win odds scale is much larger. This makes sense when we consider that the reciprocal of the odds can be interpreted as being close to a probability. If the probability of an Away Win is much less likely, then the odds increase.

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/saved-images/eda-odds-bundesliga-multipl-bookies-multiple-seasons-histograms.PNG" width="864" height="576" />
</p>

TODO: redo with same shared x scale

### 5.4 Shots

### 5.5 Shots on Target


#### Notebooks
+ [EDA - Results](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/005.001%20EDA%20-%20Results.ipynb) 

+ [EDA - Goals](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/005.002%20EDA%20-%20Goals.ipynb) 

+ [EDA - Odds](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/005.003%20EDA%20-%20Odds.ipynb) 

+ + [EDA - Shots](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/005.004%20EDA%20-%20Shots.ipynb) 
+ 
+ + [EDA - Shots on Target](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/005.005%20EDA%20-%20Shots%20on%20Target.ipynb) 



## 6. Metrics and model Diagnosis

Note on probability Calibration

### 6.1 Reliability Diagrams and Multi-Class Calibration Metrics

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


#### 6.2 Expected Calibration Error


<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/ECE-formula.png" width="559" height="108" />
</p>
See [The Importance of Calibrating Your Deep Production Model](http://alondaks.com/2017/12/31/the-importance-of-calibrating-your-deep-model/) for details

#### 6.3 Maximum Calibration Error 

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/MCE-formula.png" width="581" height="75" />
</p>

See [The Importance of Calibrating Your Deep Production Model](http://alondaks.com/2017/12/31/the-importance-of-calibrating-your-deep-model/) for details


### 6.4 Rank Probability Score

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

### 6.5 Model Diagnosis Suite

It seems there is no single number that will conveniently allow us to make a comparison between various models.

Therefore, I propose a Diagnosis Suite as follows:

+ Values for Calibration of Multi-class Results 		+ Expected Calibration Error
	+ Maximum calibration Error
+ Calibration Plots for each Class
+ RPS Distribution Plots for each Predicted Class

A sample Diagnosis suite is shown below:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/model-diagnosis-suite.png" width="731" height="668" />
</p>
 
 Explanation of how to interpret



#### Notebooks
+ [Metrics - Rank Probability Score](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/006.001%20Modeling%20Strategy%20-%20Rank%20Probability%20Score%201.ipynb) 




## 7. Data Wrangling

### 7.1 Data Flow

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/data-flow.png" width="600" height="1732" />
</p>

### 7.2 Data Splitting For Modeling

The graphic below gives an idea of the way the data is split for modeling, and the number of instances used for training and validation.

Probability calibration is done using disjoint data from training, validation, and test, to prevent over-fitting.

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/data-splitting-strategy.png" width="882" height="673" />
</p>

#### Notebooks
+ [Data Wrangling - Data Shape after Transformation](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/007.001%20Data%20Wrangling%20-%20Data%20Shape%20after%20Transformation.ipynb) 


## 8. Features

Across season features neglected

### 8.1 Model Results as Features


Obviously, a season is played in a time series sequence

A time series limits some of the models we can apply, therefore we will convert the data from a time series pattern to a supervised learning type pattern.

Consider a game played mid-season with Team A playing at home, and Team B playing away.

We believe that previous performance - for example goals scored - may help us predict the outcome of this particular game. Therefore, we could look at goals scored by each team in all their previous games, and calculate a mean for each team. However, if we did this, we would lose the ability to see each previous score.

An alternative way of organizing the data would be to transpose the previous data along the row for the game. We would be [converting the time series problem to a supervised problem](https://machinelearningmastery.com/convert-time-series-supervised-learning-problem-python/)

We would need to do this for both Team A and Team B, so we could end up with a row that looked like below:

Home Team                 |	Away Team     | Team A -1 goals scored | Team A -2 Goals scored | Team B -1 goals scored | Team B -2 Goals scored
:------------:|:------------:|:------------:|:------------:|:------------:|:------------:|
A           |	B          | 3 | 2 | 0 | 1 

The table shows that Team A in their last game scored 3 goals. In the game before that, they scored 2 goals. Team B, in their last game scored no goals, and in the game before that they scored 1 goal.


This is a start, but it ignores the difference between how well teams do playing at home, compared to when they play away. Therefore, a more nuanced scheme would be to consider each team's home and away records separately

Thgis is explained below:

So, consider a match being played today, where we want to get the full time goals - `ftGoals` scored by the home team in their previous n games

To get the **number of goals** scored by the **home team** in the **last 2 games** they played **at home**:
+ h_h_ftGoals-1
+ h_h_ftGoals-2

To get the **number of goals** scored by the **home team** in the **last 3 games** they played **away**:
+ h_a_ftGoals-1
+ h_a_ftGoals-2
+ h_a_ftGoals-3

To get the **poisson regression probability of winning** for the **away team** in the **last (1) game** they played **away**:
+ a_a_poissWin-1


#### Interpretation Note

`h_h_feat_-1` means:
+ (`h`) home team 
+ (`h`) home game records 
+ (`feat`) feature value in 
+ (`-1`) last game

The consequence of this data transposition is that we get more features as the season progresses.

This is illustrated below for a team playing away, by looking at their away full time goals record:

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/feature-fill-in-during-season.png" width="638" height="285" />
</p>

We can use this transposition to create a row for each game where the features could be corners, goals scored, implied probability, poisson regression probability etc, etc


### 8.2 Poisson Regression

The Poisson Regression used as a feature in this model is based directly on work published by [David Sheehan](https://dashee87.github.io/about/)

This page - [Predicting Football Results with Statistical Modeling](https://dashee87.github.io/football/python/predicting-football-results-with-statistical-modelling/) - runs through a method for running a Poisson Regression applied to English Premier League data

The modifications made to the original are as follows:
+ The `statsmodels` Poisson Regression model is wrapped in a scikit-learn classifier wrapper
+ The season is split up into `game days` - a game day is a day during the season when at least one soccer game is played
+ The game days are used to create a time series splitting function, so that all the prior season's results are used to predict a poisson mean for goals scored by every team playing on the current game day. The time series splitter walks through the season from beginning to end
+ At the start of the season, there is not enough data for the poission regression to run, so the predict data is filled with zeros
+ As per the original methodology, the poisson means for each team are assumed to be independent, and a probability table is formed - shown below. The probabilities for Home Win, Draw, and Away Win are then summed from the table

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/poisson-probability-table.png" width="643" height="660" />
</p>



### 8.3 Odds as Implied Probabilities

The plot below shows the distribution of home win, draw, and away win probabilities over a season.

<p>
    <img src="https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/images/implied-probabilities-distributions.png" width="640" height="433" />
</p>


These probabilities match with our previous analysis - section 5.1 where we showed that 
As shown 

Home Win                 |	Draw     | Away Win
:------------------------:|:--------------:|:------------:
0.455                   |	0.246    | 0.297


As shown in section 3.3 we can convert odds to an implied probability. In fact we can use this as a feature. Furthermore, because we are transposing the historical data, we can get the implied probability of the home team winning their last 3 home games, and compare it to the implied probabilities of the away team winning their last 3 away games. Even better, because odds are available prior to game start, we can use the odds for the current game as a feature.




#### Notebooks
+ [Features - Poisson Regression](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/008.001%20Features%20-%20Poisson%20Regression.ipynb) 

+ [Features - Poisson Distributions to Result Probabilities](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/008.002%20Features%20-%20Poisson%20Distributions%20to%20Result%20Probabilities.ipynb)

## 9. Modeling

### 9.1 Calibrated Classifiers

### 9.2 Classifiers + Probability Calibration

#### Notebooks
+ [Modeling - Calibrated Classifiers](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/009.001%20Modeling%20-%20Calibrated%20Classifiers.ipynb) 

+ [Modeling - Calibrated Classifiers + Imbalance Techniques](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/009.002%20Modeling%20-%20Calibrated%20Classifiers%20%2B%20Imbalance.ipynb)

+ [Modeling - Classifiers + Probability Calibration](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/009.003%20Modeling%20-%20Classifiers%20%2B%20Probability%20Calibration.ipynb) 

+ [Modeling - Classifiers + Probability Calibration + Imbalance Techniques](https://github.com/DMacGillivray/soccer-predictions/blob/master/notebooks/009.004%20Modeling%20-%20Classifiers%20%2B%20Probability%20Calibration%20%2B%20Imbalance.ipynb)


## 10. Model Results

### 10.1 Validation Results

### 10.2 Results on Held-Out Test Data

#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb)

## 11. Business Results

### 11.1 XXXXXXXXX

### 11.2 XXXXXXXXXX


#### Notebooks
+ [Demand Data - Compile & Review](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.01%20-%20Data%20-%20Demand%20Data%20-%20Compile%20%26%20Review.ipynb) 

+ [Demand Data - Inpute Missing Values & Deal with Outliers](https://github.com/DMacGillivray/ontario-peak-power-forecasting/blob/master/notebooks/03.02%20-%20Data%20-%20Demand%20Data%20-%20Impute%20Missing%20Values%20%26%20Deal%20with%20Outliers.ipynb) 



## 12. Conclusion


## 13. Next Steps

## 14. Software Packages


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




<br/><br/>


						David MacGillivray – Springboard Capstone Project 2 – 2 February 2020


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

