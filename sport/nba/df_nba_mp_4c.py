import pandas as pd
import random as r
import numpy as np
import pathos.multiprocessing as mp

from sport.nba.get_player_stats import player_stat_all


def df_run(player_stat_file='input/DKSalaries_20161127_6g.csv',
           NUM_SIM=1000000,
           MAX_ON=['Min', 240],
           MIN_AVG_PTS_PER_GAME=20,
           MIN_PLAYER_SALARY=3000,
           SKIP_PLAYER_LIST=[]):
    SALARY_CAP = 50000
    MIN_SALARY_USED = 49700

    def get_index_by_pos(df, pos):
        return df[df['Position'].str.contains(pos)].index

    def unique_list(l):
        return len(l) == len(set(l))

    print('NUM_SIM={}, MAX_ON={}, MIN_AVG_PTS_PER_GAME={}, MIN_PLAYER_SALARY={}, SKIP_PLAYER_LIST={}'
          .format(NUM_SIM, MAX_ON, MIN_AVG_PTS_PER_GAME, MIN_PLAYER_SALARY, SKIP_PLAYER_LIST))

    ps_dk_src = pd.read_csv(player_stat_file)
    print('Number of Players: {}'.format(len(ps_dk_src)))

    ps_nba_miner = player_stat_all()

    SKIP_PLAYER_LIST = [n.replace("'",'').replace(',','').replace('.', '') for n in SKIP_PLAYER_LIST]
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace("'", '')
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace(',', '')
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace('.', '')

    ps_dk = pd.merge(ps_dk_src, ps_nba_miner, left_on='Name', right_on='Player', how='left')

    ps_dk = ps_dk[(ps_dk['Salary'] >= MIN_PLAYER_SALARY) &
                                    (ps_dk['dk_score_implied'] >= MIN_AVG_PTS_PER_GAME) &
                                    (ps_dk['Min'] >= 30) &
                                    (np.logical_not(ps_dk['Name'].isin(SKIP_PLAYER_LIST)))]
    print('Number of Players after filter: {}'.format(len(ps_dk)))
    print()

    pg_index = get_index_by_pos(ps_dk, 'PG')
    sg_index = get_index_by_pos(ps_dk, 'SG')
    sf_index = get_index_by_pos(ps_dk, 'SF')
    pf_index = get_index_by_pos(ps_dk, 'PF')
    c_index = get_index_by_pos(ps_dk, 'C')
    g_index = get_index_by_pos(ps_dk, 'G')
    f_index = get_index_by_pos(ps_dk, 'F')
    util_index = ps_dk.index

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

        total_salary = ps_dk.loc[lineup, 'Salary'].sum()

        if total_salary > SALARY_CAP or total_salary < MIN_SALARY_USED: return

        total_max_on = ps_dk.loc[lineup, MAX_ON[0]].sum()

        if total_max_on > MAX_ON[1]:
            return [lineup, total_salary, total_max_on]

    pool = mp.Pool(4)

    results = pool.map(sim, range(NUM_SIM))

    results = [x for x in results if x]

    result = sorted(results, key=lambda a: a[2] if a else 0)

    best_result = result[-1]

    print(ps_dk.loc[best_result[0], ['Name', 'Min', 'dk_score_implied', 'AvgPointsPerGame', 'Salary']].sum())
    print(ps_dk.loc[best_result[0], ['Name', 'Min', 'dk_score_implied', 'AvgPointsPerGame']])
    print(ps_dk.loc[best_result[0], 'Name'].values)
    print()

    best_players = ps_dk.loc[best_result[0], 'Name'].values

    return best_players


out_list = ['Paul George', 'Julius Randle', 'Jeremy Lin', 'DAngelo Russell', 'Dirk Nowitzki', 'JJ Barea', 'C.J. Miles',
            'Nick Young','Deron Williams', 'Al-Farouq Aminu', 'Rondae Hollis-Jefferson', 'Larry Nance Jr.',
            'Dante Cunningham', '']
lineup_1 = df_run(SKIP_PLAYER_LIST=out_list)
lineup_2 = df_run(SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), 4))
lineup_3 = df_run(MIN_PLAYER_SALARY=4500, SKIP_PLAYER_LIST=out_list)
lineup_4 = df_run(MIN_PLAYER_SALARY=4500, SKIP_PLAYER_LIST=out_list + r.sample(lineup_3.tolist(), 4))
