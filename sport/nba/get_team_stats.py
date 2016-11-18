import platform
from bs4 import BeautifulSoup, Comment
from selenium import webdriver
import pandas as pd


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
soup_team_stats = soup.find('div', id='all_team-stats-per_game').find_all(text=lambda text:isinstance(text,Comment))[0]
team_stats_df = pd.read_html(soup_team_stats.__str__())[0]

# pt = 1
# 3pt = 0.5
# rebound = 1.25
# assist = 1.5
# steal = 2
# block = 2
# turnover = -0.5
# double-double = 1.5
# triple-double = 3
team_stats_df['DK_Score'] = team_stats_df['PTS'] + \
                            team_stats_df['3P']*0.5 + \
                            team_stats_df['TRB']*1.25 + \
                            team_stats_df['AST']*1.5 + \
                            team_stats_df['STL']*2 + \
                            team_stats_df['BLK']*2 + \
                            team_stats_df['TOV']*-0.5

# and print out the html for first game
print(team_stats_df[['Team', 'DK_Score']].iloc[:-1,:].sort(['DK_Score'],ascending=False).reset_index(drop=True))

