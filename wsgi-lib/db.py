#!/usr/bin/env python3

# system libraries
import pymysql
import multiprocessing
from os import path
import pymysqlpool
import traceback


# local libraries
from logit import logit

write_lock = multiprocessing.Lock()

pymysqlpool.logger.setLevel('WARNING')
config={'host':'*db_host*', 'user':'*db_login*', 'password':'*db_password*', 'database':'*db_name*', 'autocommit':True}

### Create a connection pool with 2 connection in it
pool1 = pymysqlpool.ConnectionPool(size=16, name='pool1', **config)

def open_sql_connection():
  #logit("open new connection")
  #traceback.print_stack()
  return pool1.get_connection()
  # return pymysql.connect(db='*db_name*',user='*db_login*',password='*db_password*',host='*db_host*',charset='utf8mb4',autocommit=True,cursorclass=pymysql.cursors.DictCursor)


def update_sql(the_sql):
    thewriteconnection = False
    try:
        write_lock.acquire()
        #logit("write lock acquired")
        thewriteconnection = open_sql_connection()
        #logit("connection acquired")
    
        cursor = thewriteconnection.cursor()
        #if cursor.execute(the_sql):
            #logit("successfully executed: {:.100}".format(the_sql))
        cursor.close()
        thewriteconnection.commit()
        #logit("transaction committed")
        thewriteconnection.close()
        #logit("connection released")
        write_lock.release()
        #logit("write lock released")
    except Exception as e:
        logit("update query {} failed {}".format(the_sql, e))
        if thewriteconnection:
            thewriteconnection.close()
        return False
    return True

    
def match_image(values):
  reetval = False
  sql = "SELECT fname,imgid, ABS(ulr-{0})+ABS(ulg-{1})+ABS(ulb-{2})+ABS(urr-{3})+ABS(urg-{4})+ABS(urb-{5})+ABS(llr-{6})+ABS(llg-{7})+ABS(llb-{8})+ABS(lrr-{9})+ABS(lrg-{10})+ABS(lrb-{11}) AS score FROM thumblist a WHERE a.fname LIKE '%jpg' ORDER BY 3 LIMIT 1".format(*(values.split(':')))
  connection = open_sql_connection()
  thecursor = connection.cursor()
  if thecursor.execute(sql) > 0:
      retval = thecursor.fetchone()
  thecursor.close()
  connection.close()
  return retval

def list_img_folders():
    retval = []
    sql = "SELECT fname FROM thumblist;"
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        for row in thecursor.fetchall():
            #logit("{}".format(row))
            thedir = path.basename(path.dirname(row[0]))
            if thedir not in retval:
                retval.append(thedir)
    thecursor.close()
    connection.close()
    return retval

def get_imgid(img_path):
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT imgid FROM thumblist WHERE fname='{}';".format(img_path)):
        imgid = cursor.fetchone()[0]
        # logit("found imgid: {}".format(imgid))
    else:
        logit("not in db: {}".format(img_path))
        imgid = False
    cursor.close()
    connection.close()
    return imgid

if __name__ == "__main__":
  connection = open_sql_connection()
  #tablecursor = connection.cursor()
  #if tablecursor.execute("show tables") > 0:
  #  for nexttable in tablecursor.fetchall():
  #    nexttablename = nexttable['Tables_in_*db_name*']
  #    print("querying {}".format(nexttablename))
  #    detailcursor = connection.cursor()
  #    if detailcursor.execute("select * from {} limit 10".format(nexttablename)) > 0:
  #      for nextrow in detailcursor.fetchall():
  #        print(nextrow)
  #    detailcursor.close()
  #tablecursor.close()
  connection.close()
  print(match_image('219:244:251:218:243:252:221:246:252:220:245:252'))
  print(list_img_folders())

