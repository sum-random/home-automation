#!/usr/bin/env python3

# system libraries
import pymysql
import multiprocessing
from os import path
import traceback
import json


# local libraries
from logit import logit
from config import config

#write_lock = multiprocessing.Lock()

CONFIG = config()['database']

def open_sql_connection():
  return pymysql.connections.Connection(**CONFIG)


def update_sql(query_string):
    thewriteconnection = False
    try:
        #write_lock.acquire()
        thewriteconnection = open_sql_connection()
    
        cursor = thewriteconnection.cursor()
        cursor.execute(query_string)
        cursor.close()
        thewriteconnection.commit()
        thewriteconnection.close()
        #write_lock.release()
    except Exception as e:
        logit("update query {} failed {}".format(query_string, e))
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

def get_first_time(host):
    thetime=False
    sql = "SELECT MIN(timestamp) AS timestamp FROM temperatures{}".format(" where host IN ('{}');".format(host) if host else "")
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        for row in thecursor.fetchall():
            thetime = row[0]
    thecursor.close()
    connection.close()
    return thetime

def get_last_time(host):
    thetime=False
    sql = "SELECT MAX(timestamp) AS timestamp FROM temperatures{}".format(" where host IN ('{}');".format(host) if host else "")
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        for row in thecursor.fetchall():
            thetime = row[0]
    thecursor.close()
    connection.close()
    return thetime

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

def set_val_for_key(key, val, asofdate=False):
    mfield = ',modified' if asofdate else ''
    mval = ",'{}'".format(asofdate) if asofdate else ''
    mupd = "modified='{}',".format(asofdate) if asofdate else ''
    query = "INSERT INTO keyval (keyname,valdata{2}) VALUES ('{0}','{1}'{3}) ON DUPLICATE KEY UPDATE {4}valdata='{1}';".format(key,val,mfield,mval,mupd)
    connection = open_sql_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.close()
    return True

def get_val_for_key(key):
    retval = ""
    query = "SELECT valdata FROM keyval WHERE keyname='{}';".format(key)
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute(query):
        retval = cursor.fetchone()[0]
    return retval

def get_vals_like_key(key):
    retval = []
    query = "SELECT keyname,valdata FROM keyval WHERE keyname LIKE '%{}%';".format(key)
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute(query):
        for row in cursor.fetchall():
            retval.append({row[0]:row[1]})
    cursor.close()
    return retval
        

if __name__ == "__main__":
  connection = open_sql_connection()
  connection.close()
  print(match_image('219:244:251:218:243:252:221:246:252:220:245:252'))
  print(list_img_folders())

