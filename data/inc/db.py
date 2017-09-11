#!/usr/bin/env python

import pymysql

def makeconnection():
  global connection
  connection = pymysql.connect(db='*db_name*',user='*db_login*',password='*db_password*',host='*db_host*',charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor)

if __name__ == "__main__":
  global connection
  makeconnection()
  tablecursor = connection.cursor()
  if tablecursor.execute("show tables") > 0:
    for nexttable in tablecursor.fetchall():
      nexttablename = nexttable['Tables_in_*db_name*']
      print("querying {}".format(nexttablename))
      detailcursor = connection.cursor()
      if detailcursor.execute("select * from {} limit 10".format(nexttablename)) > 0:
        for nextrow in detailcursor.fetchall():
          print(nextrow)
      detailcursor.close()
  tablecursor.close()
  connection.close()

