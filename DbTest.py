__author__ = 'siy'

import aig.erm.sp.db as db

sql = r'''
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
and cr.property_type = noi.property_type'''

db_conn = db.get_conn('idwdev', 'erm_riskagg', 'aig_1_amg')
result = db.exec(db_conn, sql)
db_conn.close()
all_px = map(lambda d: d['PX'], result)

print(list(all_px)[:5])

