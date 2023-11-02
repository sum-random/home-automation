#!/usr/bin/env python3

# system libraries
import pymysql
import multiprocessing
from os import path
import pymysqlpool
import traceback
import json


# local libraries
from logit import logit
from config import config

write_lock = multiprocessing.Lock()

CONFIG = config()['database']

### Create the connection pool
pool1 = pymysqlpool.ConnectionPool(size=16, name='pool1', **CONFIG)

def open_sql_connection():
  return pool1.get_connection()


def update_sql(the_sql):
    thewriteconnection = False
    try:
        #write_lock.acquire()
        thewriteconnection = open_sql_connection()
    
        cursor = thewriteconnection.cursor()
        cursor.execute(the_sql)
        cursor.close()
        thewriteconnection.commit()
        thewriteconnection.close()
        #write_lock.release()
    except Exception as e:
        logit("update query {} failed {}".format(the_sql, e))
        if thewriteconnection:
            thewriteconnection.close()
        return False
    return True

    
def match_image(values):
  retval = False
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
            thedir = path.basename(path.dirname(row[0]))
            if thedir not in retval:
                retval.append(thedir)
    thecursor.close()
    connection.close()
    return retval

def get_imgid(img_path):
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT imgid FROM thumblist WHERE fname='{}';".format(connection.escape_string(img_path))):
        imgid = cursor.fetchone()[0]
        # logit("found imgid: {}".format(imgid))
    else:
        logit("not in db: {}".format(img_path))
        imgid = False
    cursor.close()
    connection.close()
    return imgid

def get_musicid(file_path):
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT fileid FROM musicfiles WHERE filename='{}';".format(connection.escape_string(file_path))):
        fileid = cursor.fetchone()[0]
    else:
        logit("not in db: {}".format(file_path))
        fileid = False
    cursor.close()
    connection.close()
    return fileid

def save_music_file(file_name, short_name, inode, size, hash):
    fileid = False
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("INSERT INTO musicfiles(filename, shortname, inode, size, checksum) VALUES('{}', '{}', {}, {}, '{}')".format(connection.escape_string(file_name), connection.escape_string(short_name), inode, size, hash)):
        if cursor.execute("SELECT fileid FROM musicfiles WHERE filename='{}'".format(connection.escape_string(file_name))):
            fileid = cursor.fetchone()[0]
    cursor.close()   
    connection.close()
    return fileid

def del_music_row(fileid):
    connection = open_sql_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM musicfiles WHERE fileid={}".format(fileid))
    cursor.close()   
    connection.close()

        

if __name__ == "__main__":
  connection = open_sql_connection()
  connection.close()
  print(match_image('219:244:251:218:243:252:221:246:252:220:245:252'))
  print(list_img_folders())

