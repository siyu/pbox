__author__ = 'siy'

import cx_Oracle


def get_conn(db_name, username, password):
    return cx_Oracle.connect(username, password, db_name)


def exec(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)

    desc = [d[0] for d in cur.description]
    result = [dict(zip(desc, line)) for line in cur]

    cur.close()
    return result
