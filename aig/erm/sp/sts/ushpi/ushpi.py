__author__ = 'siy'

import csv
import itertools as it

print("Start generating US HPI STS csv...")

# load scenario data
scen = []
with open('scenario_us_hpi.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        scen.append(row)

# group the data by CBSA Id and keep the third months in period column
scen_grouped = {}
for k, g in it.groupby(scen, lambda d: d.get('CBSA')):
    # keep the every third month
    t = [r for r in g if (int(r.get('Period')) + 1) % 3 == 0]
    # give each qtr an index
    scen_grouped[k] = [dict(r, **{'Period_in_qtr': int((int(r.get('Period')) + 1) / 3 - 1)}) for r in t]

# for k, g in scen_grouped.items():
# print(k, g)
print('number of scenario msa: ', len(scen_grouped))

# load historical data
hist = []
with open('us_hpi_hist_2014q4.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        hist.append(row)

# group the hist data and order by period in reverse order. ie latest price comes first
hist_grouped = {}
for k, g in it.groupby(hist, lambda d: d.get('state')):
    hist_grouped[k] = sorted(g, key=lambda r: r.get('time'), reverse=True)

# for k, g in hist_grouped.items():
# print(k, g)
print('number of historical msa: ', len(hist_grouped))


# # merge hist and scenario
scen_hist_merged = {}
for cbsa, scen in scen_grouped.items():

    hist = hist_grouped.get(cbsa)
    if not hist: continue  # no historical data

    t0 = hist[0]
    if not t0.get('ticker'): continue  # no ticker

    cbsa_merged = []
    # add scenario periods
    for r in scen:
        d = {'cbsa_code': cbsa, 'cbsa_name': t0.get('ticker'),
             'period': r.get('Period_in_qtr'), 'hpi': (float(r.get('HPI')) * float(t0.get('hpiclst')))}
        cbsa_merged.append(d)

    # add historical periods
    for idx, r in enumerate(hist):
        if idx == 0: continue  # skip t0
        d = {'cbsa_code': cbsa, 'cbsa_name': r.get('ticker'),
             'period': -idx, 'hpi': r.get('hpiclst')}
        cbsa_merged.append(d)

    # sort by periods
    scen_hist_merged[cbsa] = sorted(cbsa_merged, key=lambda r: r.get('period'))

# for r in scen_hist_merged['0']:
# print(r)


# write to csv
with open('us_hpi_result.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, ['SCENARIO_AS_OF_DATE', 'SCENARIO_AS_AT_DATE', 'SUBJECT_AREA',
                                      'PARAMETER_TYPE', 'PARAMETER_NAME', 'SCENARIO_PARA_VAL_TYPE',
                                      'SCENARIO_TYPE_CODE', 'UNITS', 'DURATION_KEY',
                                      'SCENARIO_PERIOD_NUMBER', 'SCENARIO_DATATYPE_NAME', 'SCENARIO_PARA_VAL_NAME',
                                      'SCENARIO_PARAMETER_VALUE'])
    writer.writeheader()
    for cbsa, periods in scen_hist_merged.items():
        for p in periods:
            csv_row = {'SCENARIO_AS_OF_DATE': '12/31/2014',
                       'SCENARIO_AS_AT_DATE': '2/3/2015',
                       'SUBJECT_AREA': 'AGE HPI Corelogic',
                       'PARAMETER_TYPE': 'EC',
                       'PARAMETER_NAME': p.get('cbsa_name'),
                       'SCENARIO_PARA_VAL_TYPE': 'Absolute',
                       'SCENARIO_TYPE_CODE': '2015RC_Stress99p5',
                       'UNITS': 'Whole Number',
                       'DURATION_KEY': 'Q',
                       'SCENARIO_PERIOD_NUMBER': p.get('period'),
                       'SCENARIO_DATATYPE_NAME': 'Numeric',
                       'SCENARIO_PARA_VAL_NAME': 'Scenario',
                       'SCENARIO_PARAMETER_VALUE': p.get('hpi')}
            writer.writerow(csv_row)

print("Finished generating US HPI STS csv...")
