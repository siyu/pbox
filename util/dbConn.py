__author__ = 'ritzhang'

import cx_Oracle

class idwdevConn(object):
    def __init__(self, username = 'erm_riskagg', password = 'aig_1_amg'):
        self.username = username
        self.password = password
        self.dbName = 'idwdev'

    def getConnection(self):
        self.conn = cx_Oracle.connect(self.username, self.password, self.dbName)

    def runSql(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)

        desc = [d[0] for d in cur.description]
        result = [dict(zip(desc, line)) for line in cur]

        cur.close()
        return result

    def closeConnection(self):
        self.conn.close()

class idwqaConn(object):
    def __init__(self, username = 'ritzhang', password = 'RZ_1_amg'):
        self.username = username
        self.password = password
        self.dbName = 'idwqa'

    def getConnection(self):
        self.conn = cx_Oracle.connect(self.username, self.password, self.dbName)

    def runSql(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)

        desc = [d[0] for d in cur.description]
        result = [dict(zip(desc, line)) for line in cur]

        cur.close()
        return result

    def closeConnection(self):
        self.conn.close()

class idwprdConn(object):
    def __init__(self, username = 'ritzhang', password = 'RZ_1_amg'):
        self.username = username
        self.password = password
        self.dbName = 'idwprd'

    def getConnection(self):
        self.conn = cx_Oracle.connect(self.username, self.password, self.dbName)

    def runSql(self, sql):
        cur = self.conn.cursor()
        cur.execute(sql)

        desc = [d[0] for d in cur.description]
        result = [dict(zip(desc, line)) for line in cur]

        cur.close()
        return result

    def closeConnection(self):
        self.conn.close()