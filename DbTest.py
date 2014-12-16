__author__ = 'siy'

import cx_Oracle

print("db test")

con = cx_Oracle.connect('erm_riskagg', 'ErM_R15k', 'idwqa.aig.com')
cur = con.cursor()
cur.execute('select * from analytics.v_ccar_analytics_raw_erm')

row = cur.fetchone()
print(row)
cur.close()
con.close()


