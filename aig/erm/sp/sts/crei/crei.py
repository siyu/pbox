__author__ = 'siy'

import aig.erm.sp.db as db
import itertools as it

forecast_version = '2014Q2'
us_scen = 'Stress_98pct'
us_weight_apt = 0.15
us_weight_office = 0.34
us_weight_retail = 0.44
us_weight_warehouse = 0.07
us_blend_ticker = 'EC.USD.CRE.INDEX.BLEND.PPR'
euro_blend_ticker = 'EC.EUR.CRE.INDEX.BLEND.PPR'
euro_scen = 'price_99_8_th'
num_periods = 19

us_msa_sql_template = r'''
SELECT c1.forecast_period, AVG (c1.NOI / c2.CR) AS price
    FROM (  SELECT forecast_period, msa_name, cre_var_value AS NOI
              FROM erm_riskagg.cre_aig_forecast
             WHERE     forecast_version = '{forecast_version}'
                   AND msa_name IN {msa}
                   AND scenario_name = '{scenario}'
                   AND cre_var_name = 'NOI'
                   AND property_type = '{prop_type}'
          ORDER BY forecast_period) c1,
         (  SELECT forecast_period, msa_name, cre_var_value AS CR
              FROM erm_riskagg.cre_aig_forecast
             WHERE     forecast_version = '{forecast_version}'
                   AND msa_name IN {msa}
                   AND scenario_name = '{scenario}'
                   AND cre_var_name = 'CR'
                   AND property_type = '{prop_type}'
          ORDER BY forecast_period) c2
   WHERE c1.forecast_period = c2.forecast_period AND c1.msa_name = c2.msa_name
GROUP BY c1.forecast_period
ORDER BY c1.forecast_period
'''

us_blend_sql_template = r'''
SELECT c1.forecast_period, SUM (c1.weight * c1.NOI / c2.CR) AS price
    FROM (  SELECT forecast_period,
                   property_type,
                   cre_var_value AS NOI,
                   CASE
                      WHEN property_type = 'Apartment' THEN {weight_apt}
                      WHEN property_type = 'Office' THEN {weight_office}
                      WHEN property_type = 'Retail' THEN {weight_retail}
                      ELSE {weight_warehouse}
                   END
                      AS weight
              FROM erm_riskagg.cre_aig_forecast
             WHERE     forecast_version = '{forecast_version}'
                   AND msa_name = 'PPR54'
                   AND scenario_name = '{scenario}'
                   AND cre_var_name = 'NOI'
                   AND property_type IN ('Apartment',
                                         'Office',
                                         'Retail',
                                         'Warehouse')
          ORDER BY forecast_period) c1,
         (  SELECT forecast_period,
                   property_type,
                   cre_var_value AS CR,
                   CASE
                      WHEN property_type = 'Apartment' THEN {weight_apt}
                      WHEN property_type = 'Office' THEN {weight_office}
                      WHEN property_type = 'Retail' THEN {weight_retail}
                      ELSE {weight_warehouse}
                   END
                      AS weight
              FROM erm_riskagg.cre_aig_forecast
             WHERE     forecast_version = '{forecast_version}'
                   AND msa_name IN ('PPR54')
                   AND scenario_name = '{scenario}'
                   AND cre_var_name = 'CR'
                   AND property_type IN ('Apartment',
                                         'Office',
                                         'Retail',
                                         'Warehouse')
          ORDER BY forecast_period) c2
   WHERE     c1.forecast_period = c2.forecast_period
         AND c1.property_type = c2.property_type
GROUP BY c1.forecast_period
ORDER BY c1.forecast_period
'''

euro_msa_sql_template = r'''
  SELECT cre_date, AVG (price_99_8th) AS price
    FROM erm_riskagg.cre_eur_forecast ee
   WHERE     ee.metro_name IN {msa}
         AND ee.property_type = '{prop_type}'
         AND ee.forecast_version = '{forecast_version}'
         AND ee.cre_date >= '{forecast_version}'
GROUP BY cre_date
ORDER BY cre_date
'''

euro_blend_sql_template = r'''
SELECT ret.cre_date,
       (ret.price_99_8th + offi.price_99_8th + ware.price_99_8th) / 3
          AS price
  FROM (  SELECT cre_date, price_99_8th AS price_99_8th
            FROM erm_riskagg.cre_eur_forecast ee
           WHERE     ee.metro_name IN ('PPR Europe')
                 AND ee.property_type = 'Retail'
                 AND ee.forecast_version = '{forecast_version}'
        ORDER BY cre_date) ret,
       (  SELECT cre_date, price_99_8th AS price_99_8th
            FROM erm_riskagg.cre_eur_forecast ee
           WHERE     ee.metro_name IN ('PPR Europe')
                 AND ee.property_type = 'Office'
                 AND ee.forecast_version = '{forecast_version}'
        ORDER BY cre_date) offi,
       (  SELECT cre_date, price_99_8th AS price_99_8th
            FROM erm_riskagg.cre_eur_forecast ee
           WHERE     ee.metro_name IN ('PPR Europe')
                 AND ee.property_type = 'Warehouse'
                 AND ee.forecast_version = '{forecast_version}'
        ORDER BY cre_date) ware
 WHERE     ware.cre_date = offi.cre_date
       AND offi.cre_date = ret.cre_date
       AND offi.cre_date >= '{forecast_version}'
'''

us_scen_map = [{'msa': "('New York', 'Philadelphia', 'Wilmington')", 'prop_type': 'Apartment',
                'ticker': 'EC.USD.CRE.INDEX.APT.NJ_PA_DE.PPR'},
               {'msa': "('Dallas - Fort Worth','Los Angeles')", 'prop_type': 'Office',
                'ticker': 'EC.USD.CRE.INDEX.OFFICE.LA_DALLAS.PPR'},
               {'msa': "('Houston')", 'prop_type': 'Office', 'ticker': 'EC.USD.CRE.INDEX.OFFICE.Houston.PPR'},
               {'msa': "('Los Angeles')", 'prop_type': 'Office', 'ticker': 'EC.USD.CRE.INDEX.OFFICE.LA.PPR'},
               {'msa': "('Los Angeles')", 'prop_type': 'Warehouse', 'ticker': 'EC.USD.CRE.INDEX.WAREHOUSE.LA.PPR'},
               {'msa': "('San Francisco')", 'prop_type': 'Office', 'ticker': 'EC.USD.CRE.INDEX.OFFICE.SF.PPR'},
               {'msa': "('PPR54')", 'prop_type': 'Warehouse', 'ticker': 'EC.USD.CRE.INDEX.WAREHOUSE.PPR'},
               {'msa': "('PPR54')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.PPR'},
               {'msa': "('PPR54')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.PPR'},
               {'msa': "('Los Angeles')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.LosAngeles.PPR'},
               {'msa': "('Tampa')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.TAMPA.PPR'},
               {'msa': "('San Diego')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.SanDiego.PPR'},
               {'msa': "('Seattle')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Seattle.PPR'},
               {'msa': "('San Jose')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.SanJose.PPR'},
               {'msa': "('San Francisco')", 'prop_type': 'Apartment',
                'ticker': 'EC.USD.CRE.INDEX.APT.SanFrancisco.PPR'},
               {'msa': "('Orlando')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Orlando.PPR'},
               {'msa': "('New York')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.NewYork.PPR'},
               {'msa': "('Mobile')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Mobile.PPR'},
               {'msa': "('Minneapolis')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Minneapolis.PPR'},
               {'msa': "('Miami')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Miami.PPR'},
               {'msa': "('Denver')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Denver.PPR'},
               {'msa': "('Dallas - Fort Worth')", 'prop_type': 'Apartment',
                'ticker': 'EC.USD.CRE.INDEX.APT.Dallas.PPR'},
               {'msa': "('Charleston SC')", 'prop_type': 'Apartment',
                'ticker': 'EC.USD.CRE.INDEX.APT.Charleston SC.PPR'},
               {'msa': "('Boston')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Boston.PPR'},
               {'msa': "('Baton Rouge')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Baton Rouge.PPR'},
               {'msa': "('Atlanta')", 'prop_type': 'Apartment', 'ticker': 'EC.USD.CRE.INDEX.APT.Atlanta.PPR'},
               {'msa': "('Washington - NoVA - MD')", 'prop_type': 'Apartment',
                'ticker': 'EC.USD.CRE.INDEX.APT.WashNoVaMd.PPR'},
               {'msa': "('Jacksonville')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Jacksonville.PPR'},
               {'msa': "('Atlanta')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Atlanta.PPR'},
               {'msa': "('Greensboro')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Greensboro.PPR'},
               {'msa': "('Myrtle Beach')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.MyrtleBeach.PPR'},
               {'msa': "('New York')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.NewYork.PPR'},
               {'msa': "('Orlando')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Orlando.PPR'},
               {'msa': "('San Diego')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.SanDiego.PPR'},
               {'msa': "('Seattle')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Seattle.PPR'},
               {'msa': "('Washington - NoVA - MD')", 'prop_type': 'Retail',
                'ticker': 'EC.USD.CRE.INDEX.RETAIL.WashNoVaMd.PPR'},
               {'msa': "('Tampa')", 'prop_type': 'Retail', 'ticker': 'EC.USD.CRE.INDEX.RETAIL.Tampa.PPR'},
               {'msa': "('Chattanooga')", 'prop_type': 'Warehouse',
                'ticker': 'EC.USD.CRE.INDEX.Warehouse.Chattanooga.PPR'},
               {'msa': "('Fort Wayne')", 'prop_type': 'Warehouse',
                'ticker': 'EC.USD.CRE.INDEX.Warehouse.FortWayne.PPR'},
               {'msa': "('San Diego')", 'prop_type': 'Warehouse', 'ticker': 'EC.USD.CRE.INDEX.Warehouse.SanDiego.PPR'}]

euro_msa_map = [
    {'msa': "('Warsaw','Moscow')", 'prop_type': 'Office', 'ticker': 'EC.RUB_PLN.CRE.INDEX.OFFICE.MOSCOW_WARSAW.PPR'},
    {'msa': "('Moscow')", 'prop_type': 'Office', 'ticker': 'EC.RUB.CRE.INDEX.OFFICE.MOSCOW.PPR'},
    {'msa': "('Warsaw')", 'prop_type': 'Office', 'ticker': 'EC.PLN.CRE.INDEX.OFFICE.WARSAW.PPR'},
    {'msa': "('PPR Europe')", 'prop_type': 'Warehouse', 'ticker': 'EC.EUR.CRE.INDEX.WAREHOUSE.PPR'},
    {'msa': "('PPR Europe')", 'prop_type': 'Retail', 'ticker': 'EC.EUR.CRE.INDEX.RETAIL.PPR'}, ]


# query the db for result and limit the first num_records of results
def get_result(db_conn, sql, num_records):
    result = db.exec(db_conn, sql)
    # take the first <num_records> of elements
    return list(it.islice(result, num_records))


db_conn = db.get_conn('idwdev', 'erm_riskagg', 'aig_1_amg')
output = []

# US MSA
for m in us_scen_map:
    sql = us_msa_sql_template.format(scenario=us_scen, msa=m['msa'],
                                     forecast_version=forecast_version, prop_type=m['prop_type'])
    rs = get_result(db_conn, sql, num_periods)
    rs = [dict(r, **{'TICKER': m['ticker']}) for r in rs]
    output.append(rs)

# US Blend
us_blend_sql = us_blend_sql_template.format(scenario=us_scen, forecast_version=forecast_version,
                                            weight_apt=us_weight_apt, weight_office=us_weight_apt,
                                            weight_retail=us_weight_retail, weight_warehouse=us_weight_warehouse)
us_blend_res = get_result(db_conn, us_blend_sql, num_periods)
us_blend_res = [dict(r, **{'TICKER': us_blend_ticker}) for r in us_blend_res]
output.append(us_blend_res)

# Euro MSA
for m in euro_msa_map:
    sql = euro_msa_sql_template.format(scenario=euro_scen, msa=m['msa'],
                                       forecast_version=forecast_version, prop_type=m['prop_type'])
    rs = get_result(db_conn, sql, num_periods)
    rs = [dict(r, **{'TICKER': m['ticker'], 'PRICE': float(r['PRICE']) / float(rs[0]['PRICE'])}) for r in rs]
    output.append(rs)

# Euro Blend
euro_blend_sql = euro_blend_sql_template.format(forecast_version=forecast_version)
euro_blend_res = get_result(db_conn, euro_blend_sql, num_periods)
euro_blend_res = [
    dict(r, **{'TICKER': euro_blend_ticker, 'PRICE': float(r['PRICE']) / float(euro_blend_res[0]['PRICE'])}) for r in
    euro_blend_res]
output.append(euro_blend_res)

db_conn.close()

for i in output:
    print(i)
