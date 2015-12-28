import pandas as pd
import numpy as np
import statsmodels.api as sm

team_scores_url = 'http://www.basketball-reference.com/leagues/NBA_2016_games.html'
team_stats_url = 'http://www.basketball-reference.com/leagues/NBA_2016.html'


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

# team_stats.loc[team_stats['Team']=='Golden State Warriors'].iloc[:,2:].values - team_stats.loc[team_stats['Team']=='Cleveland Cavaliers'].iloc[:,2:].values

print('done')
