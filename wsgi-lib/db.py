#!/usr/bin/env python3

# system libraries
import pymysql
import multiprocessing
from os import path

# local libraries
from logit import logit

theconnections = {}
thewriteconnection = False

write_lock = multiprocessing.Lock()

def open_sql_connection():
  return pymysql.connect(db='*db_name*',user='*db_login*',password='*db_password*',host='*db_host*',charset='utf8mb4',autocommit=True,cursorclass=pymysql.cursors.DictCursor)


def update_sql(the_sql):
    write_lock.acquire()
    logit("write lock acquired")
    if not thewriteconnection:
       thewriteconnection = open_sql_connection()

    cursor = thewriteconnection.cursor()
    if cursor.execute(the_sql):
        logit("successfully executed: {:.100}".format(the_sql))
    cursor.close()
    thewriteconnection.commit()
    logit("transaction committed")
    write_lock.release()
    logit("write lock released")

    
def get_sql_connection(force_new=False):
  thepid = multiprocessing.current_process().pid
  # logit("Get db connection for {} current open connections {} according to pymysql {}".format(thepid, theconnections.keys(), pymysql.connections))
  if not thepid in theconnections:
      logit("New connection for {}".format(thepid))
      theconnections[thepid] = open_sql_connection()
  elif not theconnections[thepid].ping():
      logit("Reopen connection for {}".format(thepid))
      theconnections[thepid] = open_sql_connection()
  elif force_new:
      if thepid in theconnections:
          logit("Closing old connection {} for {}".format(theconnections[thepid], thepid))
          theconnections[thepid].close()
      logit("Force reopen connection for {}".format(thepid))
      theconnections[thepid] = open_sql_connection()
  #logit("{} returning {} from {}".format(thepid, str(theconnections[thepid])[:100], theconnections.keys()))
  return theconnections[thepid]

def match_image(values):
  sql = "SELECT fname,imgid, ABS(ulr-{0})+ABS(ulg-{1})+ABS(ulb-{2})+ABS(urr-{3})+ABS(urg-{4})+ABS(urb-{5})+ABS(llr-{6})+ABS(llg-{7})+ABS(llb-{8})+ABS(lrr-{9})+ABS(lrg-{10})+ABS(lrb-{11}) AS score FROM thumblist a WHERE a.fname LIKE '%jpg' ORDER BY 3 LIMIT 1".format(*(values.split(':')))
  connection = get_sql_connection()
  with connection.cursor() as thecursor:
      if thecursor.execute(sql) > 0:
          return thecursor.fetchone()
  return {'imgid': sql}

def list_img_folders():
    retval = []
    sql = "SELECT fname FROM thumblist;"
    connection = get_sql_connection()
    with connection.cursor() as thecursor:
        if thecursor.execute(sql) > 0:
            for row in thecursor.fetchall():
                thedir = path.basename(path.dirname(row['fname']))
                if thedir not in retval:
                    retval.append(thedir)
    return retval
            
if __name__ == "__main__":
  connection = get_sql_connection()
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
  #connection.close()
  print(match_image('219:244:251:218:243:252:221:246:252:220:245:252'))
  print(list_img_folders())

