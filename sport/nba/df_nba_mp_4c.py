import pandas as pd
import random as r
import numpy as np
import pathos.multiprocessing as mp


def df_run(player_stat_file='input/DKSalaries_20161125_5g_late.csv',
           NUM_SIM=5000000,
           MIN_TOTAL_TARGET_PTS=260,
           MIN_AVG_PTS_PER_GAME=20,
           MIN_PLAYER_SALARY=3200,
           SKIP_PLAYER_LIST=[]):

    SALARY_CAP = 50000
    MIN_SALARY_USED = 49700

    def get_index_by_pos(df, pos):
        return df[df['Position'].str.contains(pos)].index

    def unique_list(l):
        return len(l) == len(set(l))

    print('NUM_SIM={}, MIN_TOTAL_TARGET_PTS={}, MIN_AVG_PTS_PER_GAME={}, MIN_PLAYER_SALARY={}, SKIP_PLAYER_LIST={}'
          .format(NUM_SIM, MIN_TOTAL_TARGET_PTS, MIN_AVG_PTS_PER_GAME, MIN_PLAYER_SALARY, SKIP_PLAYER_LIST))

    player_stat_df = pd.read_csv(player_stat_file)
    print('Number of Players: {}'.format(len(player_stat_df)))
    player_stat_df['P/S'] = player_stat_df['AvgPointsPerGame'] / player_stat_df['Salary'] * 1000

    player_stat_df = player_stat_df[(player_stat_df['Salary'] >= MIN_PLAYER_SALARY) &
                                    (player_stat_df['AvgPointsPerGame'] > MIN_AVG_PTS_PER_GAME) &
                                    (player_stat_df['P/S'] >= 4.5) &
                                    (np.logical_not(player_stat_df['Name'].isin(SKIP_PLAYER_LIST)))]
    print('Number of Players after filter: {}'.format(len(player_stat_df)))
    print()

    pg_index = get_index_by_pos(player_stat_df, 'PG')
    sg_index = get_index_by_pos(player_stat_df, 'SG')
    sf_index = get_index_by_pos(player_stat_df, 'SF')
    pf_index = get_index_by_pos(player_stat_df, 'PF')
    c_index = get_index_by_pos(player_stat_df, 'C')
    g_index = get_index_by_pos(player_stat_df, 'G')
    f_index = get_index_by_pos(player_stat_df, 'F')
    util_index = player_stat_df.index

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

    result = sorted(results, key=lambda a: a[2] if a else 0)

    best_result = result[-1]
    best_result = [player_stat_df.loc[best_result[0], 'Name'].values, best_result[1], best_result[2]]

    print(best_result)
    print()

    return best_result

out_list = ['J.J. Barea', 'Greg Monroe', 'Joel Embiid', 'Justise Winslow', 'Deron Williams'
            'Reggie Jackson', 'Joakim Noah', 'Julius Randle', "D'Angelo Russell", 'T.J. Warren',
            'Danilo Gallinari','Will Barton','Al-Farouq Aminu', 'Nick Young', '']
lineup_1 = df_run(SKIP_PLAYER_LIST=out_list)
lineup_2 = df_run(SKIP_PLAYER_LIST=out_list+lineup_1[0][:4].tolist())
lineup_3 = df_run(SKIP_PLAYER_LIST=out_list+lineup_1[0][4:].tolist())
lineup_4 = df_run(SKIP_PLAYER_LIST=out_list+lineup_1[0].tolist())