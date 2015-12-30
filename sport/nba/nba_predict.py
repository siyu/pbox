import pandas as pd
import numpy as np
import statsmodels.api as sm

team_scores_url = 'http://www.basketball-reference.com/leagues/NBA_2016_games.html'
team_stats_url = 'http://www.basketball-reference.com/leagues/NBA_2016.html'
team_misc_stats_url = 'http://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fleagues%2FNBA_2016.html&div=div_misc&del_col=1'
team_ranking_url = 'http://widgets.sports-reference.com/wg.fcgi?css=1&site=bbr&url=%2Fleagues%2FNBA_2016_ratings.html&div=div_ratings&del_col=1'


def get_team_scores(url):
    s = pd.read_html(url)[0]
    s = s[np.isfinite(s['PTS'])]
    s = s.reset_index(drop=True)
    del s['Start (ET)']
    del s['Unnamed: 2']
    del s['Unnamed: 7']
    del s['Notes']
    return s


def get_games_by_date(url, date_str):
    s = pd.read_html(url)[0]
    s = s[s['Date'] == date_str]
    return s[['Home/Neutral', 'Visitor/Neutral']].values


def get_team_stats(url):
    s = pd.read_html(url)[6]
    return s.iloc[:-1, :]


def get_team_misc_stats(url):
    s = pd.read_html(url)[8]
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


def predict_by_stats(games=[]):
    scores = get_team_scores(team_scores_url)
    num_scores = len(scores)
    team_stats = pd.read_html(team_misc_stats_url, header=1)[0].iloc[:-1, :]
    scores['home-away'] = scores['PTS.1'] - scores['PTS'] - 2  # home court adv = 2 pts

    param_columns = team_stats.columns[13:21].tolist()  # starts from column eFG%
    param_columns.remove('FT/FGA')
    param_columns.remove('FT/FGA.1')
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
    print()

    team_ranking = pd.read_html(team_ranking_url, header=1)[0]

    print('{:22s} - {:22s} =  {:7s} | {:7s}'.format('home', 'away', 'fit mov', 'ref mov'))
    for [home, away] in games:
        spread = sum(result.params * (
            team_stats.loc[team_stats['Team'] == home][param_columns].values -
            team_stats.loc[team_stats['Team'] == away][
                param_columns].values)[0])
        mov = team_ranking.loc[team_stats['Team'] == home]['MOV/A'].values - \
              team_ranking.loc[team_stats['Team'] == away]['MOV/A'].values + 2

        print('{:22s} - {:22s} =  {:7.1f} | {:7.1f}'.format(home, away, spread, mov[0]))


games = get_games_by_date(team_scores_url, 'Wed, Dec 30, 2015')
predict_by_stats(games)
print()
