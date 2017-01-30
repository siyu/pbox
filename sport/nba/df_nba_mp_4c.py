import pandas as pd
import random as rand
import numpy as np
import pathos.multiprocessing as mp
import operator

from sport.nba.get_player_stats import player_stat_all, injury_list, player_gamelog, player_name_norm


# TODO:
# + filter by team
# + use vegas projected team score as multiplier
# + pick players from team with more injured players
# + report lineup with most injured team mates



def df_run(ps_nba_miner,
           player_stat_file='input/DKSalaries_20170129_6g.csv',
           NUM_SIM=500000,  # default 1M
           MAX_ON=[operator.ge, 'Min', 230],
           MAX_COST_PER_PT_OVERRIDE=np.nan,  # default np.nan, 2015-2016:203
           MIN_AVG_PTS_PER_GAME=15,  # default 15
           MIN_MINUTE=15,  # deafult 15
           SKIP_PLAYER_LIST=[],
           PREFILLED_PLAYERS={'PG': None, 'SG': None, 'SF': None, 'PF': None, 'C': None, 'G': None, 'F': None,
                              'UTIL': None}):
    SALARY_CAP = 50000
    MIN_SALARY_USED = 40000  # default 49500
    MIN_PLAYER_SALARY = 3000

    def get_index_by_pos(df, pos):
        return df[df['Position'].str.contains(pos)].index

    def get_index_by_name(df, name):
        return df[df['Name'] == name].index.values

    def unique_list(l):
        return len(l) == len(set(l))

    print('NUM_SIM={}, MAX_ON={}, MIN_AVG_PTS_PER_GAME={}, MIN_PLAYER_SALARY={}, SKIP_PLAYER_LIST={}'
          .format(NUM_SIM, MAX_ON, MIN_AVG_PTS_PER_GAME, MIN_PLAYER_SALARY, SKIP_PLAYER_LIST))

    ps_dk_src = pd.read_csv(player_stat_file)
    print('Number of Players: {}'.format(len(ps_dk_src)))

    SKIP_PLAYER_LIST = [player_name_norm(n) for n in SKIP_PLAYER_LIST]
    ps_dk_src['Name'] = ps_dk_src['Name'].str.replace("[',.-]", '')

    ps_dk_merged = pd.merge(ps_dk_src, ps_nba_miner, left_on='Name', right_on='Player', how='left')

    ps_dk_merged['salary/dk_score_calc'] = np.round((ps_dk_merged['Salary'] / ps_dk_merged['dk_score_calc']), 1)
    ps_dk_merged['cost_eff'] = ps_dk_merged['pts/min'] / ps_dk_merged['Salary'] * 1000

    ps_dk_tmp = ps_dk_merged[(ps_dk_merged['Salary'] >= MIN_PLAYER_SALARY) &
                             (ps_dk_merged['dk_score_calc'] >= MIN_AVG_PTS_PER_GAME) &
                             (ps_dk_merged['Min'] >= MIN_MINUTE) &
                             (np.logical_not(ps_dk_merged['Name'].isin(SKIP_PLAYER_LIST)))
                             | ps_dk_merged['Name'].isin(PREFILLED_PLAYERS.values())]

    print('Number of Players after first filter: {}'.format(len(ps_dk_tmp)))

    cost_pt_mean = ps_dk_tmp['salary/dk_score_calc'].replace(np.inf, np.nan).dropna().mean()
    cost_pt_std = ps_dk_tmp['salary/dk_score_calc'].replace(np.inf, np.nan).dropna().std()
    # MAX_COST_PER_PT = cost_pt_mean - cost_pt_std / 6 if np.isnan(MAX_COST_PER_PT_OVERRIDE) else MAX_COST_PER_PT_OVERRIDE
    MAX_COST_PER_PT = cost_pt_mean if np.isnan(MAX_COST_PER_PT_OVERRIDE) else MAX_COST_PER_PT_OVERRIDE

    print('After first filter: cost_pt_mean={}, cost_pt_std={}, MAX_COST_PER_PT={}'
          .format(cost_pt_mean, cost_pt_std, MAX_COST_PER_PT))

    ps_dk = ps_dk_tmp[
        (ps_dk_tmp['salary/dk_score_calc'] <= MAX_COST_PER_PT) | ps_dk_tmp['Name'].isin(PREFILLED_PLAYERS.values())]
    print('Number of Players after MAX_COST_PER_PT filter: {}'.format(len(ps_dk)))

    ps_dk = ps_dk_tmp

    for i, row in ps_dk.iterrows():
        new_stat = player_gamelog(row['Player'])
        ps_dk.loc[i, 'score_mean'] = round(new_stat['mean'], 2)
        ps_dk.loc[i, 'score_std'] = round(new_stat['std'], 2)
        ps_dk.loc[i, 'score_norm'] = round(new_stat['std'] / new_stat['mean'], 2)

    print()

    for i, row in ps_dk.iterrows():
        print('{:20}  {:<6}  {:<6}  min={:<6}  avg_score={:<6}  std/mean={:<6}  salary/fp={:<6}'
              .format(row['Player'],
                      row['Position'],
                      row['Salary'],
                      row['Min'],
                      row['score_mean'],
                      row['score_norm'],
                      row['salary/dk_score_calc']))

    print()

    pg_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('PG')) or get_index_by_pos(ps_dk, 'PG')
    sg_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('SG')) or get_index_by_pos(ps_dk, 'SG')
    sf_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('SF')) or get_index_by_pos(ps_dk, 'SF')
    pf_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('PF')) or get_index_by_pos(ps_dk, 'PF')
    c_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('C')) or get_index_by_pos(ps_dk, 'C')
    g_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('G')) or get_index_by_pos(ps_dk, 'G')
    f_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('F')) or get_index_by_pos(ps_dk, 'F')
    util_index = get_index_by_name(ps_dk_src, PREFILLED_PLAYERS.get('UTIL')) or ps_dk.index

    def sim(i):
        lineup = [rand.choice(pg_index),
                  rand.choice(sg_index),
                  rand.choice(sf_index),
                  rand.choice(pf_index),
                  rand.choice(c_index),
                  rand.choice(g_index),
                  rand.choice(f_index),
                  rand.choice(util_index)]

        # prevent one play in more than one position
        if not unique_list(lineup): return

        # prevent more than two players from same team
        if ps_dk.loc[lineup, 'teamAbbrev'].value_counts().max() > 2: return

        total_salary = ps_dk.loc[lineup, 'Salary'].sum()

        if total_salary > SALARY_CAP or total_salary < MIN_SALARY_USED: return

        total_max_on = ps_dk.loc[lineup, MAX_ON[1]].sum()

        if MAX_ON[0](total_max_on, MAX_ON[2]):
            return (lineup, total_salary, round(total_max_on, 1))

    pool = mp.Pool(4)

    results = pool.map(sim, range(NUM_SIM))

    results = [x for x in results if x]

    results_sorted = sorted(results, key=lambda a: a[2])

    for r in results_sorted[-100:-1]:
        print('{} min({:.0f}) std({:.1f})'.format(r,
                                                  ps_dk.loc[r[0], 'Min'].sum(),
                                                  np.sqrt(np.power(ps_dk.loc[r[0], 'score_std'], 2).sum())))
        print(ps_dk.loc[r[0], 'Name'].values)
        print()


out_list = injury_list() + ['Channing Frye', 'Manu Ginobili', 'Ish Smith', 'Rajon Rondo']

ps_nba_miner = player_stat_all()

df_run(ps_nba_miner,
       #MAX_ON=[operator.le, 'score_norm', 100],
       MAX_ON=[operator.ge, 'dk_score_calc', 220],
       SKIP_PLAYER_LIST=out_list,
       # PREFILLED_PLAYERS={'PG': None, 'SG': None, 'SF': None, 'PF': None, 'C': 'Zaza Pachulia', 'G': None, 'F': None, 'UTIL': None}
       PREFILLED_PLAYERS={'PG': None, 'SG': None, 'SF': None, 'PF': None, 'C': None, 'G': None, 'F': None, 'UTIL': None}
       )
