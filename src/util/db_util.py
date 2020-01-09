# -*- coding:utf-8 -*-
import MySQLdb
import yaml

class MysqldbHelper:
    #获取数据库连接
    def __init__(self):
        file = open("config/config.yaml")
        config = yaml.load(file)
        file.close()
        env = config["currentEnv"]

        self.host = config[env]["mysql_host"]
        self.user = config[env]["mysql_user"]
        self.passwd = config[env]["mysql_passwd"]
        self.db = config[env]["mysql_database"]
    def getCon(self):
        try:
            conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.db,port=3306,charset='utf8')
            return conn
        except MySQLdb.Error as e:
            print ("Mysqldb Error:%s" % e)
    #查询方法，使用con.cursor(MySQLdb.cursors.DictCursor),返回结果为字典    
    def select(self,sql):
        try:
            con=self.getCon()
            print (con)
            cur=con.cursor(MySQLdb.cursors.DictCursor)
            count=cur.execute(sql)
            fc=cur.fetchall()
            return fc
        except MySQLdb.Error as e:
            print ("Mysqldb Error:%s" % e)
        finally:
            cur.close()
            con.close()
    #带参数的更新方法,eg:sql='insert into pythontest values(%s,%s,%s,now()',params=(6,'C#','good book')
    def updateByParam(self,sql,params):
        try:
            con=self.getCon()
            cur=con.cursor()
            count=cur.execute(sql,params)
            con.commit()
            return count
        except MySQLdb.Error as e:
            con.rollback()
            print ("Mysqldb Error:%s" % e)
        finally:
            cur.close()
            con.close()
    #不带参数的更新方法
    def update(self,sql):
        try:
            con=self.getCon()
            cur=con.cursor()
            count=cur.execute(sql)
            con.commit()
            return count
        except MySQLdb.Error as e:
            con.rollback()
            print ("Mysqldb Error:%s" % e)
        finally:
            cur.close()
            con.close()
            
