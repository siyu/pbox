__author__ = 'siy'

import aig.erm.sp.plot as p
import aig.erm.sp.db as db
import itertools as it

sql_legacy = r'''
select cr.*, noi.CRE_VAR_VALUE/cr.CRE_var_value px from (
       select * from
              cre_aig_forecast
              where CRE_VAR_NAME = 'CR') cr,
       (select * from
              cre_aig_forecast
              where CRE_VAR_NAME = 'NOI') noi
where cr.forecast_version = '2013Q4'
and cr.scenario_name = 'Stress_99p8pct'
and cr.MSA_NAME = 'PPR54'
and cr.forecast_version = noi.forecast_version
and cr.scenario_name = noi.scenario_name
and cr.forecast_period = noi.forecast_period
and cr.msa_name = noi.msa_name
and cr.property_type = noi.property_type
order by cr.msa_name, cr.scenario_name, cr.property_type, cr.forecast_period'''

result_legacy = result = db.db_get('idwdev', 'erm_riskagg', 'aig_1_amg', sql_legacy)

sql_improved = r'''
select cr.*, noi.CRE_VAR_VALUE/cr.CRE_var_value px from (
       select * from
              cre_aig_forecast_dev
              where CRE_VAR_NAME = 'CR') cr,
       (select * from
              cre_aig_forecast_dev
              where CRE_VAR_NAME = 'NOI') noi
where cr.forecast_version = '2014Q4'
and cr.scenario_name = 'Stress_99p8pct'
and cr.MSA_NAME = 'PPR54'
and cr.forecast_version = noi.forecast_version
and cr.scenario_name = noi.scenario_name
and cr.forecast_period = noi.forecast_period
and cr.msa_name = noi.msa_name
and cr.property_type = noi.property_type
order by cr.msa_name, cr.scenario_name, cr.property_type, cr.forecast_period'''

result_improved = db.db_get('idwdev', 'erm_riskagg', 'aig_1_amg', sql_improved)

num_data_pts = 48
# filter by property type
print(len([item for item in result_improved if item['PROPERTY_TYPE'] == 'Apartment']))

periods = list(it.islice(map(lambda d: d['FORECAST_PERIOD'], result_legacy), num_data_pts))
px_legacy = list(it.islice(map(lambda d: d['PX'], result_legacy), num_data_pts))
px_improved = list(it.islice(map(lambda d: d['PX'], result_improved),num_data_pts))

series = [{'x': periods, 'y': px_legacy, 'marker': '-', 'label': 'Legacy'},
          {'x': periods, 'y': px_improved, 'marker': '-', 'label': 'Improved'}]

p.plot('AIG', 'Period', 'Price', series)