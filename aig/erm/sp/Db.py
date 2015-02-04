__author__ = 'siy'

import cx_Oracle


def db_get(db_name, username, password, sql):

    con = cx_Oracle.connect(username, password, db_name)
    cur = con.cursor()
    cur.execute(sql)

    desc = [d[0] for d in cur.description]
    result = [dict(zip(desc, line)) for line in cur]

    cur.close()
    con.close()

    return result