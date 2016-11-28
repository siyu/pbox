import platform
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
import pandas as pd


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
    ps_df['Player'] = ps_df['Player'].str.replace("'", '')
    ps_df['Player'] = ps_df['Player'].str.replace(',', '')
    ps_df['Player'] = ps_df['Player'].str.replace('.', '')

    # normalize names
    ps_df['Player'] = ps_df['Player'].str.replace('Jose Juan Barea', 'JJ Barea')
    ps_df['Player'] = ps_df['Player'].str.replace('Glenn Robinson', 'Glenn Robinson III')
    ps_df['Player'] = ps_df['Player'].str.replace('Kelly Oubre', 'Kelly Oubre Jr')
    ps_df['Player'] = ps_df['Player'].str.replace('Nene', 'Nene Hilario')
    ps_df['Player'] = ps_df['Player'].str.replace('Juan Hernangomez', 'Juancho Hernangomez')
    ps_df['Player'] = ps_df['Player'].str.replace('Willy Hernangomez', 'Guillermo Hernangomez')
    ps_df['Player'] = ps_df['Player'].str.replace('Luc Mbah a Moute', 'Luc Richard Mbah a Moute')

    return ps_df
    # pt = 1
    # 3pt = 0.5
    # rebound = 1.25
    # assist = 1.5
    # steal = 2
    # block = 2
    # turnover = -0.5
    # double-double = 1.5
    # triple-double = 3

    # team_stats_df['DK_Score'] = team_stats_df['PTS'] + \
    #                             team_stats_df['3P']*0.5 + \
    #                             team_stats_df['TRB']*1.25 + \
    #                             team_stats_df['AST']*1.5 + \
    #                             team_stats_df['STL']*2 + \
    #                             team_stats_df['BLK']*2 + \
    #                             team_stats_df['TOV']*-0.5
    #
    #


def player_stat_all():
    player_basic_stat_df = load_player_stat(
        'http://www.nbaminer.com/nbaminer_nbaminer/basic_stats_pl.php?operation=eexcel&partitionpage=&partition2page=&page=1')
    player_adv_stat_df = load_player_stat(
        'http://www.nbaminer.com/nbaminer_nbaminer/advanced_player_stats.php?operation=eexcel&partitionpage=&partition2page=&page=1')

    player_stat_df = pd.merge(player_basic_stat_df, player_adv_stat_df, on='Player')

    player_stat_df['dk_score_implied'] = player_stat_df['Pts'].astype(float) + \
                                         player_stat_df['3PTM'].astype(float) * 0.5 + \
                                         player_stat_df['Reb'].astype(float) * 1.25 + \
                                         player_stat_df['Ast'].astype(float) * 1.5 + \
                                         player_stat_df['Stl'].astype(float) * 2 + \
                                         player_stat_df['Blk'].astype(float) * 2 + \
                                         player_stat_df['TO'].astype(float) * -0.5

    player_stat_df['Min'] = player_stat_df['Min'].astype(float)

    # player_stat_df.plot(kind='scatter', x='Min', y='dk_score_implied')

    return player_stat_df


def injury_list():
    df = pd.read_html('http://www.cbssports.com/nba/injuries/daily')
    t = df[0]
    t.columns = t.iloc[1]
    t = t.reindex(t.index.drop(0))
    t = t.reindex(t.index.drop(1))
    players = t['Player'].values.tolist()

    return [p.replace("'", '').replace(',', '').replace('.', '') for p in players]
