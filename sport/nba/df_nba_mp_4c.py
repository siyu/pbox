import pandas as pd
import random as r
import numpy as np
import pathos.multiprocessing as mp

from sport.nba.get_player_stats import player_stat_all, injury_list


# TODO:
# + fix player on a position
# + pick players from team with more injured players
# + strategy: pick players with high mean low std + players from teams with injured players


def df_run(ps_nba_miner,
           player_stat_file='input/DKSalaries_20161209_9g.csv',
           NUM_SIM=1000000,  # default 1M
           MAX_ON=['Min', 240],
           MAX_COST_PER_PT_OVERRIDE=np.nan,  # default np.nan, 2015-2016:203
           MIN_AVG_PTS_PER_GAME=15,  # default 15
           MIN_MINUTE=15,  # deafult 15
           SKIP_PLAYER_LIST=[]):

    SALARY_CAP = 50000
    MIN_SALARY_USED = 49500         # default 49500
    MIN_PLAYER_SALARY = 3000

    def get_index_by_pos(df, pos):
        return df[df['Position'].str.contains(pos)].index

    def unique_list(l):
        return len(l) == len(set(l))

    print('NUM_SIM={}, MAX_ON={}, MIN_AVG_PTS_PER_GAME={}, MIN_PLAYER_SALARY={}, SKIP_PLAYER_LIST={}'
          .format(NUM_SIM, MAX_ON, MIN_AVG_PTS_PER_GAME, MIN_PLAYER_SALARY, SKIP_PLAYER_LIST))

    ps_dk_src = pd.read_csv(player_stat_file)
    print('Number of Players: {}'.format(len(ps_dk_src)))

    SKIP_PLAYER_LIST = [n.replace("'", '').replace(',', '').replace('.', '') for n in SKIP_PLAYER_LIST]
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace("'", '')
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace(',', '')
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace('.', '')

    ps_dk_merged = pd.merge(ps_dk_src, ps_nba_miner, left_on='Name', right_on='Player', how='left')

    ps_dk_merged['salary/dk_score_calc'] = np.round((ps_dk_merged['Salary'] / ps_dk_merged['dk_score_calc']), 1)
    ps_dk_merged['cost_eff'] = ps_dk_merged['pts/min'] / ps_dk_merged['Salary'] * 1000

    ps_dk_tmp = ps_dk_merged[(ps_dk_merged['Salary'] >= MIN_PLAYER_SALARY) &
                             (ps_dk_merged['dk_score_calc'] >= MIN_AVG_PTS_PER_GAME) &
                             (ps_dk_merged['Min'] >= MIN_MINUTE) &
                             (np.logical_not(ps_dk_merged['Name'].isin(SKIP_PLAYER_LIST)))]

    print('Number of Players after first filter: {}'.format(len(ps_dk_tmp)))

    cost_pt_mean = ps_dk_tmp['salary/dk_score_calc'].replace(np.inf, np.nan).dropna().mean()
    cost_pt_std = ps_dk_tmp['salary/dk_score_calc'].replace(np.inf, np.nan).dropna().std()
    MAX_COST_PER_PT = cost_pt_mean - cost_pt_std / 3 if np.isnan(MAX_COST_PER_PT_OVERRIDE) else MAX_COST_PER_PT_OVERRIDE

    print('After first filter: cost_pt_mean={}, cost_pt_std={}, MAX_COST_PER_PT={}'
          .format(cost_pt_mean, cost_pt_std, MAX_COST_PER_PT))

    ps_dk = ps_dk_tmp[ps_dk_merged['salary/dk_score_calc'] <= MAX_COST_PER_PT]

    print('Number of Players after MAX_COST_PER_PT filter: {}'.format(len(ps_dk)))
    print('Players remain after MAX_COST_PER_PT filter:\n {}'.format(
        ps_dk_merged.loc[ps_dk.index, ['Player', 'Salary', 'Min', 'dk_score_calc', 'salary/dk_score_calc']].values))
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

        # prevent one play in more than one position
        if not unique_list(lineup): return

        # prevent more than two players from same team
        if ps_dk.loc[lineup, 'teamAbbrev'].value_counts().max() > 2: return

        total_salary = ps_dk.loc[lineup, 'Salary'].sum()

        if total_salary > SALARY_CAP or total_salary < MIN_SALARY_USED: return

        total_max_on = ps_dk.loc[lineup, MAX_ON[0]].sum()

        if total_max_on >= MAX_ON[1]:
            return [lineup, total_salary, total_max_on]

    pool = mp.Pool(4)

    results = pool.map(sim, range(NUM_SIM))

    results = [x for x in results if x]

    result = max(results, key=lambda a: a[2])

    best_result = result

    print(ps_dk.loc[best_result[0], ['Name', 'Min', 'dk_score_calc', 'AvgPointsPerGame', 'Salary']].sum())
    print(ps_dk.loc[best_result[0], ['Name', 'Min', 'dk_score_calc', 'AvgPointsPerGame', 'Salary']])
    print(ps_dk.loc[best_result[0], 'Name'].values)
    print()

    best_players = ps_dk.loc[best_result[0], 'Name'].values

    return best_players


out_list = injury_list() + ['Channing Frye', 'Manu Ginobili', 'Pau Gasol']

ps_nba_miner = player_stat_all()

lineup_rotate_size = 3

lineup_1 = df_run(ps_nba_miner, MAX_ON=['cost_eff', 1], SKIP_PLAYER_LIST=out_list)
lineup_1 = df_run(ps_nba_miner, MAX_ON=['cost_eff', 1], SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))
lineup_1 = df_run(ps_nba_miner, MAX_ON=['cost_eff', 1], SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))
lineup_1 = df_run(ps_nba_miner, MAX_ON=['cost_eff', 1], SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))
lineup_1 = df_run(ps_nba_miner, SKIP_PLAYER_LIST=out_list)
lineup_1 = df_run(ps_nba_miner, SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))
lineup_1 = df_run(ps_nba_miner, SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))
lineup_1 = df_run(ps_nba_miner, SKIP_PLAYER_LIST=out_list + r.sample(lineup_1.tolist(), lineup_rotate_size))



# lineup_1 = df_run(SKIP_PLAYER_LIST=out_list)
