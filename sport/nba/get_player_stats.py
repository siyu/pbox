import platform
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
import pandas as pd
import numpy as np


def load_player_stat(url):
    # PhantomJS files have different extensions
    # under different operating systems
    if platform.system() == 'Windows':
        PHANTOMJS_PATH = './phantomjs.exe'
    else:
        PHANTOMJS_PATH = './phantomjs'

    # here we'll use pseudo browser PhantomJS,
    # but browser can be replaced with browser = webdriver.FireFox(),
    # which is good for debugging.
    browser = webdriver.PhantomJS(PHANTOMJS_PATH)
    # browser.get('http://www.basketball-reference.com/leagues/NBA_2017.html#team-stats-base::none')
    browser.get(url)

    # let's parse our html
    soup = BeautifulSoup(browser.page_source, "html.parser")
    browser.quit()

    ps_df = pd.read_html(soup.__str__())[0]

    # use first row as header
    ps_df.columns = ps_df.columns = ps_df.iloc[0]
    ps_df = ps_df.reindex(ps_df.index.drop(0))

    # remove special characters in player name
    ps_df['Player'] = ps_df['Player'].str.replace("[',.-]", '')

    # normalize names
    ps_df['Player'] = ps_df['Player'].str.replace('Jose Juan Barea', 'JJ Barea')
    ps_df['Player'] = ps_df['Player'].str.replace('Glenn Robinson', 'Glenn Robinson III')
    ps_df['Player'] = ps_df['Player'].str.replace('Kelly Oubre', 'Kelly Oubre Jr')
    ps_df['Player'] = ps_df['Player'].str.replace('Nene', 'Nene Hilario')
    ps_df['Player'] = ps_df['Player'].str.replace('Juan Hernangomez', 'Juancho Hernangomez')
    ps_df['Player'] = ps_df['Player'].str.replace('Willy Hernangomez', 'Guillermo Hernangomez')
    ps_df['Player'] = ps_df['Player'].str.replace('Luc Mbah a Moute', 'Luc Richard Mbah a Moute')

    return ps_df


def player_stat_all():
    player_basic_stat_df = load_player_stat(
        'http://www.nbaminer.com/nbaminer_nbaminer/basic_stats_pl.php?operation=eexcel&partitionpage=&partition2page=&page=1')
    player_adv_stat_df = load_player_stat(
        'http://www.nbaminer.com/nbaminer_nbaminer/advanced_player_stats.php?operation=eexcel&partitionpage=&partition2page=&page=1')

    player_stat_df = pd.merge(player_basic_stat_df, player_adv_stat_df, on='Player')

    player_stat_df['dk_score_calc'] = player_stat_df['Pts'].astype(float) + \
                                      player_stat_df['3PTM'].astype(float) * 0.5 + \
                                      player_stat_df['Reb'].astype(float) * 1.25 + \
                                      player_stat_df['Ast'].astype(float) * 1.5 + \
                                      player_stat_df['Stl'].astype(float) * 2 + \
                                      player_stat_df['Blk'].astype(float) * 2 + \
                                      player_stat_df['TO'].astype(float) * -0.5 + \
                                      player_stat_df['Double Doubles'].astype(float) * 1.5 / player_stat_df[
                                          'Games_y'].astype(float) + \
                                      player_stat_df['Triple Doubles'].astype(float) * 3 / player_stat_df[
                                          'Games_y'].astype(float)

    player_stat_df['dk_score_calc'] = np.round(player_stat_df['dk_score_calc'], 1)

    player_stat_df = player_stat_df.loc[player_stat_df['dk_score_calc'] != player_stat_df['dk_score_calc'].min()]
    player_stat_df = player_stat_df.loc[player_stat_df['dk_score_calc'] != player_stat_df['dk_score_calc'].max()]

    player_stat_df['Min'] = player_stat_df['Min'].astype(float)
    player_stat_df['pts/min'] = player_stat_df['dk_score_calc'] / player_stat_df['Min']

    # player_stat_df.plot(kind='scatter', x='Min', y='dk_score_calc')

    return player_stat_df


def injury_list():
    df = pd.read_html('http://www.cbssports.com/nba/injuries/daily')
    t = df[0]
    t.columns = t.iloc[1]
    t = t.reindex(t.index.drop(0))
    t = t.reindex(t.index.drop(1))
    players = t['Player'].values.tolist()

    return [player_name_norm(p) for p in players]


def player_name_norm(player_name):
    return player_name.replace("'", '').replace(',', '').replace('.', '').replace('-', '')


def player_gamelog(player_name):
    name_codes = {'Marcus Williams': '04',
                  'Marvin Williams': '02',
                  'Kemba Walker': '02',
                  'Bojan Bogdanovic': '02',
                  'Harrison Barnes': '02',
                  'Gerald Henderson': '02',
                  'Anthony Davis': '02',
                  'Marcus Morris': '03',
                  'Matt Barnes': '02',
                  'Brandon Knight': '03',
                  'Wesley Matthews': '02',
                  'Lou Williams': '02',
                  'Isaiah Thomas': '02',
                  'Tobias Harris': '02',
                  'Markieff Morris': '02',
                  'David Lee': '02',
                  'Andre Roberson': '03',
                  'Joe Johnson': '02',
                  'Jeff Green': '02',
                  'Danny Green': '02'}
    code = name_codes.get(player_name, '01')
    p_names = player_name.split(' ')
    name_in_url = p_names[len(p_names) - 1][:5] + p_names[0][:2] + code

    if player_name == 'Clint Capela':
        name_in_url = 'capelca01'
    elif player_name == 'Larry Nance Jr':
        name_in_url = 'nancela02'
    elif player_name == 'JJ Barea':
        name_in_url = 'bareajo01'
    elif player_name == 'Tim Hardaway Jr':
        name_in_url = 'hardati02'

    # p = pd.read_html('http://www.basketball-reference.com/players/w/westbru01/gamelog/2017/')[7]
    url = 'http://www.basketball-reference.com/players/w/{}/gamelog/2017/'.format(name_in_url)
    print(player_name, url)
    p = pd.read_html(url)[7]

    # remove extra rows
    p = p[(p['GS'].astype(str) == '1') | (p['GS'].astype(str) == '0')]

    p['dk_score_calc'] = p['PTS'].astype(float) + \
                         p['3P'].astype(float) * 0.5 + \
                         p['TRB'].astype(float) * 1.25 + \
                         p['AST'].astype(float) * 1.5 + \
                         p['STL'].astype(float) * 2 + \
                         p['BLK'].astype(float) * 2 + \
                         p['TOV'].astype(float) * -0.5

    for i, r in p.iterrows():
        doubles = sum([int(i) for i in [float(r['PTS']) >= 10,
                                        float(r['TRB']) >= 10,
                                        float(r['AST']) >= 10,
                                        float(r['STL']) >= 10,
                                        float(r['BLK']) >= 10]])
        if doubles > 2:
            p.loc[i, 'dk_score_calc'] += 4.5
        elif doubles > 1:
            p.loc[i, 'dk_score_calc'] += 1.5

    # remove one min and one max to lessen outlier effect
    p = p.loc[p['dk_score_calc'] != p['dk_score_calc'].min()]
    p = p.loc[p['dk_score_calc'] != p['dk_score_calc'].max()]

    return {'mean': p['dk_score_calc'].mean(), 'std': p['dk_score_calc'].std(), 'hist': p}


def get_team_stat():
    # PhantomJS files have different extensions
    # under different operating systems
    if platform.system() == 'Windows':
        PHANTOMJS_PATH = './phantomjs.exe'
    else:
        PHANTOMJS_PATH = './phantomjs'

    # here we'll use pseudo browser PhantomJS,
    # but browser can be replaced with browser = webdriver.FireFox(),
    # which is good for debugging.
    browser = webdriver.PhantomJS(PHANTOMJS_PATH)
    # browser.get('http://www.basketball-reference.com/leagues/NBA_2017.html#team-stats-base::none')
    browser.get('http://www.basketball-reference.com/leagues/NBA_2017.html')

    # let's parse our html
    soup = BeautifulSoup(browser.page_source, "html.parser")
    # get all the games
    soup_team_stats = \
        soup.find('div', id='all_team-stats-per_game').find_all(text=lambda text: isinstance(text, Comment))[0]
    team_stats_df = pd.read_html(soup_team_stats.__str__())[0]
    return team_stats_df


def get_team_multiple(date_yyyymmdd):
    teams_stat = get_team_stat()
    teams_str = 'Golden State Warriors|Portland Trail Blazers|Houston Rockets|Los Angeles Lakers|Los Angeles Clippers|Toronto Raptors|Indiana Pacers|Charlotte Hornets|Denver Nuggets|New Orleans Pelicans|Phoenix Suns|Detroit Pistons|Oklahoma City Thunder|New York Knicks|Atlanta Hawks|Cleveland Cavaliers|Orlando Magic|Utah Jazz|Memphis Grizzlies|Boston Celtics|Minnesota Timberwolves|San Antonio Spurs|Brooklyn Nets|Sacramento Kings|Miami Heat|Chicago Bulls|Washington Wizards|Milwaukee Bucks|Philadelphia 76ers|Dallas Mavericks'
    teams_regex = '({})({})'.format(teams_str, teams_str)
    odd_url = 'http://www.donbest.com/nba/odds/{}.html'.format(date_yyyymmdd)
    odd_df = pd.read_html(odd_url)[0]
    odd_df.columns = odd_df.iloc[1]
    odd_df = odd_df.reindex(odd_df.index.drop(0))
    odd_df = odd_df.reindex(odd_df.index.drop(1))

    team_mult = {}

    for i, r in odd_df.iterrows():
        teams = 1

    # TODO: PK, -/+ in front

    return

    # get_team_multiple('20161216')
