import pymysql
import time,json

# mysql地址
MySQLServerIP = "111.230.177.71"
MySQLPort = 3306
MySQLUser = "root"
MySQLPasswd = "LxyZFTT@1492"

class simpleManager():
    def __init__(self,ip=MySQLServerIP,port=MySQLPort,user=MySQLUser,passwd=MySQLPasswd):
        self.host = ip
        self.port = port
        self.user = user
        self.passwd = passwd
        self.cursor = None
        self.conn = None
        self.db = None
        self.charset = "utf8"
        self.needCommit = False

    def connectMySQLServer(self,db=None,charset=None):
        if db==None:
            if self.db!=None:
                if isinstance(self.db,str):
                    db = self.db
        if charset==None:
            if self.charset!=None:
                if isinstance(self.charset,str):
                    charset = self.charset
            else:
                charset = "utf8"
        if not isinstance(charset,str):
            charset = "utf8"
        self.conn = pymysql.connect(host=self.host,user=self.user,passwd=self.passwd,db=db,charset=charset)
        self.cursor = self.conn.cursor()
        self.db = db

    def excute(self,sql):
        if isinstance(sql,str):
            if isinstance(self.cursor,pymysql.cursors.Cursor):
                self.cursor.execute(sql)
                self.needCommit = True
                r = self.cursor.fetchall()
                return r
        return None

    def useDataBase(self,db):
        if isinstance(db,str):
            sql = "use "+db+";"
            r = self.excute(sql)
            return r
        return -1

    def listDataBase(self):
        sql = "show databases;"
        r = self.excute(sql)
        return r

    def listTables(self,db=None):
        if db==None:
            try:
                r = self.excute("show tables;")
                return r
            except:
                return -1
        if isinstance(db,str):
            self.useDataBase(db)
            sql = "show tables;"
            r = self.excute(sql)
            return r
        return -1

    def commit(self):
        self.conn.commit()
        self.needCommit = False

    def closeCursor(self):
        try:
            self.cursor.close()
            return 0
        except:
            return -1

    def closeConnection(self):
        if self.needCommit:
            self.commit()
        try:
            self.conn.close()
            return 0
        except:
            return -1

    def close(self):
        print("close cursor:",self.closeCursor())
        print("close connection:",self.closeConnection())

    def getAllDataFromTables(self,table,db=None):
        if db!=None:
            if isinstance(db,str):
                self.useDataBase(db)
        sql = "select * from "+table+";"
        r = self.excute(sql)
        return r

    def dropTables(self,table,db=None):
        if db!=None:
            self.useDataBase(db)
        sql = "DROP TABLE "+table+";"
        return self.excute(sql)

    def dropDataBase(self,db):
        sql = "drop database "+db+";"
        return self.excute(sql)


    def getValue(self,table,object_=None,where=None,db=None):
        if db!=None:
            self.useDataBase(db)
        selectTable = ""
        if isinstance(table,list):
            for each in table:
                if isinstance(each,str):
                    selectTable += each+","
            selectTable = selectTable[:-1]
        else:
            selectTable = table
        sql = "SELECT "
        if object_!=None:
            if isinstance(object_,str):
                sql += object_+" from "+selectTable
            else:
                sql += "* from "+selectTable
        else:
            sql += "* from "+selectTable
        if where!=None:
            sql += " WHERE "+where+";"
        else:
            sql += ";"
        r = self.excute(sql)
        return r

    def createDataBase(self,db):
        if isinstance(db,str):
            sql = "CREATE DATABASE "+db
            return self.excute(sql)
        return -1

    def judgeDtataBaseExist(self,db):
        r = self.listDataBase()
        for each in r:
            if db in each:
                return True
        return False

    def judgeTableExist(self,table,db=None):
        r = self.listTables(db)
        for each in r:
            if table in each:
                return True
        return False


class mySQL_Server(simpleManager):
    def uploadData(self,data):
        stamp = data["stamp"]
        data = data["data"]
        jsonData = json.dumps(data)
        # jsonData = jsonData.replace("\\","\\\\")
        # jsonData = jsonData.replace("\\","\\\\")
        tableName = self.getTableName(stamp)
        if not self.judgeTableExist(tableName):
            self.createNewTable(name=tableName)
        sql = "INSERT INTO {0} (getTime,jsonData)VALUES ({1},{2})".format(tableName,str(stamp),jsonData)
        self.excute(sql)

    def createNewTable(self,name):
        # sql = """CREATE TABLE IF NOT EXISTS {0}(
        # getTime FLOAT ,
        # jsonData LONGTEXT,
        # PRIMARY KEY(getTime),
        # )""".format(name)

        sql = """CREATE TABLE IF NOT EXISTS {0}(
            getTime FLOAT NOT NULL,
            JsonData LONGTEXT,
            PRIMARY KEY(getTime)
            );""".format(name)

        self.excute(sql)

    def init(self):
        self.db = "GoldSliver"
        self.connectMySQLServer(db=self.db)

    def getTableName(self,timeStamp=None):
        if timeStamp==None:
            timeStamp = time.time()
        t = time.localtime(timeStamp)
        year = t.tm_year
        mon = t.tm_mon
        day = t.tm_mday
        hour = t.tm_hour
        min_ = t.tm_min
        sec = t.tm_sec
        name = str(year)
        if mon<10:
            name = name+"0"+str(mon)
        else:
            name = name+str(mon)
        if day<10:
            name = name+"0"+str(day)
        else:
            name = name+str(day)
        name = "tb"+name
        return name



if __name__ == '__main__':
    manager = simpleManager()
    manager.connectMySQLServer()
    # manager.useDataBase("GoldSliver")
    # sql = """CREATE TABLE IF NOT EXISTS {0}(
    # getTime FLOAT NOT NULL,
    # JsonData LONGTEXT,
    # PRIMARY KEY(getTime)
    # );""".format("tb20191111")
    # # sql = "CREATE TABLE IF NOT EXISTS 'test'('id' CHAR[10] NOT NULL ,'value' FLOAT,PRIMARY KEY('id'))ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    # # manager.excute(sql)
    # # manager.commit()
    # print(manager.listTables())
    # sql = """DROP TABLE tb20191111;"""
    # manager.excute(sql)
    # manager.commit()
    # print(manager.listTables())
    # manager.close()
