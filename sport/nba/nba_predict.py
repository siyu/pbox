import pandas as pd
import numpy as np
import statsmodels.api as sm

team_scores_url = 'http://www.basketball-reference.com/leagues/NBA_2016_games.html'
team_stats_url = 'http://www.basketball-reference.com/leagues/NBA_2016.html'
team_misc_url = 'nba_misc_stats.csv'


def get_team_scores(url):
    s = pd.read_html(url)[0]
    s = s[np.isfinite(s['PTS'])]
    s = s.reset_index(drop=True)
    del s['Start (ET)']
    del s['Unnamed: 2']
    del s['Unnamed: 7']
    del s['Notes']
    return s


def get_team_stats(url):
    s = pd.read_html(url)[6]
    return s.iloc[:-1, :]


def get_team_misc_stats():
    s = pd.read_csv(team_misc_url)
    return s.iloc[:-1, :]


def predict_rank():
    scores = get_team_scores(team_scores_url)
    num_scores = len(scores)
    team_stats = get_team_stats(team_stats_url)
    teams = sorted(team_stats['Team'].values)
    num_teams = len(teams)
    scores['home-away'] = scores['PTS.1'] - scores['PTS'] - 2  # home court adv = 2 pts
    x = np.zeros([num_scores, num_teams])

    for idx, row in scores.iterrows():
        home = row['Home/Neutral']
        away = row['Visitor/Neutral']
        home_idx = teams.index(home)
        away_idx = teams.index(away)
        x[idx][home_idx] = 1
        x[idx][away_idx] = -1

    x = pd.DataFrame(x, columns=teams)
    y = scores['home-away']
    model = sm.OLS(y, x)
    result = model.fit()
    print(result.summary())


def predict_by_stats():
    scores = get_team_scores(team_scores_url)
    num_scores = len(scores)
    team_stats = get_team_misc_stats()
    scores['home-away'] = scores['PTS.1'] - scores['PTS'] - 2  # home court adv = 2 pts

    # param_columns = ['FTr',	'3PAr',	'TS%',	'eFG%',	'TOV%',	'ORB%',	'FT/FGA',	'eFG%',	'TOV%',	'DRB%',	'FT/FGA']
    param_columns = ['FTr',	'TS%',	'eFG%',	'TOV%',	'ORB%',	'FT/FGA',	'eFG%',	'TOV%',		'FT/FGA']
    num_params = len(param_columns)
    x = np.zeros([num_scores, num_params])

    for idx, row in scores.iterrows():
        home = row['Home/Neutral']
        away = row['Visitor/Neutral']
        x[idx] = team_stats.loc[team_stats['Team'] == home][param_columns].values - \
                 team_stats.loc[team_stats['Team'] == away][param_columns].values

    x = pd.DataFrame(x, columns=param_columns)
    y = scores['home-away']
    model = sm.OLS(y, x)
    result = model.fit()
    print(result.summary())

# team_stats.loc[team_stats['Team']=='Golden State Warriors'][param_columns].values - team_stats.loc[team_stats['Team']=='Cleveland Cavaliers'][param_columns].values

predict_by_stats()
predict_rank()

print('done')
