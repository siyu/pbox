import pandas as pd
import random as r
import datetime as dt
import numpy as np
import multiprocessing as mp

SALARY_CAP = 50000
MIN_SALARY_USED = 49700
NUM_SIM = 500000
MIN_TOTAL_TARGET_PTS = 270
MIN_AVG_PTS_PER_GAME = 20
MIN_PLAYER_SALARY = 3200
SKIP_PLAYER_LIST = ['Jerryd Bayless', 'Avery Bradley', 'Al Horford', 'LeBron James']


def get_index_by_pos(df, pos):
    return df[df['Position'].str.contains(pos)].index


def unique_list(l):
    return len(l) == len(set(l))


player_stat_df = pd.read_csv('input/DKSalaries.csv')
print('Number of Players: {}'.format(len(player_stat_df)))
player_stat_df['P/S'] = player_stat_df['AvgPointsPerGame'] / player_stat_df['Salary'] * 1000

player_stat_df = player_stat_df[(player_stat_df['Salary'] >= MIN_PLAYER_SALARY) &
                                (player_stat_df['AvgPointsPerGame'] > MIN_AVG_PTS_PER_GAME) &
                                (player_stat_df['P/S'] >= 4.5) &
                                (np.logical_not(player_stat_df['Name'].isin(SKIP_PLAYER_LIST)))]
print('Number of Players after filter: {}'.format(len(player_stat_df)))

pg_index = get_index_by_pos(player_stat_df, 'PG')
sg_index = get_index_by_pos(player_stat_df, 'SG')
sf_index = get_index_by_pos(player_stat_df, 'SF')
pf_index = get_index_by_pos(player_stat_df, 'PF')
c_index = get_index_by_pos(player_stat_df, 'C')
g_index = get_index_by_pos(player_stat_df, 'G')
f_index = get_index_by_pos(player_stat_df, 'F')
util_index = player_stat_df.index

results = []

start_time = dt.datetime.now()
bad_lineup_count = 0


def sim(i):
    lineup = [r.choice(pg_index),
              r.choice(sg_index),
              r.choice(sf_index),
              r.choice(pf_index),
              r.choice(c_index),
              r.choice(g_index),
              r.choice(f_index),
              r.choice(util_index)]

    if not unique_list(lineup): return

    total_salary = player_stat_df.loc[lineup, 'Salary'].sum()

    if total_salary > SALARY_CAP or total_salary < MIN_SALARY_USED: return

    total_pts = player_stat_df.loc[lineup, 'AvgPointsPerGame'].sum()

    if total_pts > MIN_TOTAL_TARGET_PTS:
        return [lineup, total_salary, total_pts]


pool = mp.Pool(4)

results = pool.map(sim, range(NUM_SIM))
results = [x for x in results if x]

for l, s, p in results:
    print(player_stat_df.loc[l, 'Name'].values, s, p)
    print()

end_time = dt.datetime.now()

print('Number of Seconds used: {:.0f}'.format((end_time - start_time).total_seconds()))
