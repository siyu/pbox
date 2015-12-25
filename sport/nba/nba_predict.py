import pandas as pd
import numpy as np

team_scores_url = 'http://www.basketball-reference.com/leagues/NBA_2016_games.html'
team_stats_url = 'http://www.basketball-reference.com/leagues/NBA_2016.html'


def get_team_scores(url):
    s = pd.read_html(url)[0]
    s = s[np.isfinite(s['PTS'])]
    del s['Start (ET)']
    del s['Unnamed: 2']
    del s['Unnamed: 7']
    del s['Notes']
    return s


def get_team_stats(url):
    s = pd.read_html(url)[6]
    return s


scores = get_team_scores(team_scores_url)
team_stats = get_team_stats(team_stats_url)

print('done')
