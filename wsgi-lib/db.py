#!/usr/bin/env python3
"""database functionality helper, migrate all SQL into this module"""

# system libraries
from os import path
#import multiprocessing
#import traceback
#import json
import pymysql


# local libraries
from logit import logit
from config import config

#write_lock = multiprocessing.Lock()

CONFIG = config()['database']

def open_sql_connection():
    """Return a connection from the pool"""
    return pymysql.connections.Connection(**CONFIG)


def update_sql(query_string):
    """Execute an UPDATE or INSERT statement"""
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
        logit(f"update query {query_string} failed {e}")
        if thewriteconnection:
            thewriteconnection.close()
        return False
    return True

def match_image(values):
    """Collage function, find an image whose color quadrant values match the input"""
    retval=False
    # this is an artifact of older bash code, needs to be redone
    rgbarr=values.split(':')
    sql=f"""
SELECT fname,imgid,
       ABS(ulr-{rgbarr[0]})+ABS(ulg-{rgbarr[1]})+ABS(ulb-{rgbarr[2]})+
       ABS(urr-{rgbarr[3]})+ABS(urg-{rgbarr[4]})+ABS(urb-{rgbarr[5]})+
       ABS(llr-{rgbarr[6]})+ABS(llg-{rgbarr[7]})+ABS(llb-{rgbarr[8]})+
       ABS(lrr-{rgbarr[9]})+ABS(lrg-{rgbarr[10]})+ABS(lrb-{rgbarr[11]}) AS score 
FROM thumblist a 
WHERE a.fname LIKE '%jpg' 
ORDER BY 3 LIMIT 1"""
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        retval = thecursor.fetchone()
    thecursor.close()
    connection.close()
    return retval

def get_first_time(host=False):
    """Returns the lowest timestamp value from temperatures table"""
    thetime=False
    whereclause=" WHERE host IN ('{host}');" if host else ""
    sql = f"""
SELECT MIN(timestamp) AS timestamp
FROM temperatures
{whereclause}"""
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        for row in thecursor.fetchall():
            thetime = row[0]
    thecursor.close()
    connection.close()
    return thetime

def get_last_time(host=False):
    """Returns the highest timestamp value from temperatures table"""
    thetime=False
    whereclause=f" WHERE host IN ('{host}');" if host else ""
    sql = f"""
SELECT MAX(timestamp) AS timestamp
FROM temperatures
{whereclause}"""
    connection = open_sql_connection()
    thecursor = connection.cursor()
    if thecursor.execute(sql) > 0:
        for row in thecursor.fetchall():
            thetime = row[0]
    thecursor.close()
    connection.close()
    return thetime

def list_img_folders():
    """Return a list of folders for the image viewer"""
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
    """Return the database id of an image file or False if not found"""
    connection = open_sql_connection()
    cursor = connection.cursor()
    eimg_path=connection.escape_string(img_path)
    sql=f"""
SELECT imgid
FROM thumblist
WHERE fname='{eimg_path}';"""
    if cursor.execute(sql):
        imgid = cursor.fetchone()[0]
        # logit("found imgid: {}".format(imgid))
    else:
        logit(f"not in db: {img_path}")
        imgid = False
    cursor.close()
    connection.close()
    return imgid

def get_musicid(file_path):
    """Return the database id of an audio file or False if not found"""
    connection = open_sql_connection()
    cursor = connection.cursor()
    efile_path=connection.escape_string(file_path)
    sql=f"""
SELECT fileid
FROM musicfiles
WHERE filename='{efile_path}';"""
    if cursor.execute(sql):
        fileid = cursor.fetchone()[0]
    else:
        logit(f"not in db: {file_path}")
        fileid = False
    cursor.close()
    connection.close()
    return fileid

def save_music_file(file_name, short_name, inode, size, hashval):
    """Save information about a new audio file"""
    fileid = False
    connection = open_sql_connection()
    cursor = connection.cursor()
    efile_name=connection.escape_string(file_name)
    eshort_name=connection.escape_string(short_name)
    sql=f"""
INSERT INTO musicfiles(filename, shortname, inode, size, checksum)
VALUES('{efile_name}', '{eshort_name}', {inode}, {size}, '{hashval}')"""
    if cursor.execute(sql):
        if cursor.execute(f"""
SELECT fileid
FROM musicfiles
WHERE filename='{efile_name}'"""):
            fileid = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    return fileid

def del_music_row(fileid):
    """Remove db entry for deleted file"""
    connection = open_sql_connection()
    cursor = connection.cursor()
    cursor.execute(f"DELETE FROM musicfiles WHERE fileid={fileid}")
    cursor.close()
    connection.close()

# implement mongodb in SQL
def set_val_for_key(key, val, asofdate=False):
    """Change the value for a key"""
    mfield = ',modified' if asofdate else ''
    mval = f",'{asofdate}'" if asofdate else ''
    mupd = f"modified='{asofdate}'," if asofdate else ''
    query = f"""
INSERT INTO keyval (keyname,valdata{mfield})
VALUES ('{key}','{val}'{mval})
ON DUPLICATE KEY UPDATE {mupd}valdata='{val}';"""
    connection = open_sql_connection()
    cursor = connection.cursor()
    cursor.execute(query)
    connection.close()
    return True

def get_val_for_key(key):
    """Retrieve value for key"""
    retval = ""
    query = f"SELECT valdata FROM keyval WHERE keyname='{key}';"
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute(query):
        retval = cursor.fetchone()[0]
    return retval

def get_vals_like_key(key):
    """Fuzzy search for key, return array of matches"""
    retval = []
    query = f"SELECT keyname,valdata FROM keyval WHERE keyname LIKE '%{key}%';"
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute(query):
        for row in cursor.fetchall():
            retval.append({row[0]:row[1]})
    cursor.close()
    return retval

#lightcontrol helpers
def get_light_list():
    """Return array of light names and ids"""
    lights={}
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT lightid, lightname FROM lightnames"):
        for nextrow in cursor.fetchall():
            lights[nextrow[0]] = nextrow[1]
    cursor.close()
    connection.close()
    return lights

def get_light_state_ids(light=-1):
    """Maps light code back to db id, this is mostly for X10"""
    retval = []
    connection = open_sql_connection()
    cursor = connection.cursor()
    if light == -1:
        where = '' #  all light codes
    else:
        where = f" WHERE lightcode={light}"
    if cursor.execute(f"SELECT id FROM lightschedule{where}"):
        for nextrow in cursor.fetchall():
            retval.append(nextrow[0])
    cursor.close()
    connection.close()
    return retval

def get_desired_light_states(light):
    """return current setting for one or all lights"""
    retval = ['id\tdescr']
    connection = open_sql_connection()
    cursor = connection.cursor()
    if light == -1:
        where = '' #  all light codes
    else:
        where = f" WHERE lightcode={light}"
    if cursor.execute(f"""
SELECT id, lightcode, monthmatch, daymatch, turnon, turnoff, hhcode
FROM lightschedule{where}"""):
        for nextrow in cursor.fetchall():
            retval.append(f"""
{nextrow[0]}\tHousecode: {nextrow[6]} Month: {nextrow[2]} Day: {nextrow[3]} Turn On: {nextrow[4]} Turn Off: {nextrow[5]}""")
    cursor.close()
    connection.close()
    return retval

def get_light_schedule_detail(lightid):
    """retrieve all the light schedule entries for one light"""
    retval = {}
    connection = open_sql_connection()
    cursor = connection.cursor()
    if cursor.execute(f"""
SELECT id, lightcode, monthmatch, daymatch, turnon, turnoff, hhcode
FROM lightschedule
WHERE id={lightid}"""):
        for nextrow in cursor.fetchall():
            retval = {'id': nextrow[0],\
                      'lightcode': nextrow[1],\
                      'monthmatch': nextrow[2],\
                      'daymatch': nextrow[3],\
                      'turnon': nextrow[4],\
                      'turnoff': nextrow[5],\
                      'hhcode': nextrow[6]}
    cursor.close()
    connection.close()
    return retval

def set_light_schedule_detail(lightid, hhcode, lightcode, month, day, on_time, off_time, is_new):
    """create or update a new light schedule item"""
    connection = open_sql_connection()
    cursor = connection.cursor()
    if is_new == 'true':
        query_string = f"""
INSERT INTO lightschedule (hhcode, lightcode, monthmatch, daymatch, turnon, turnoff)
VALUES ('{hhcode}', '{lightcode}', '{month}', '{day}', '{on_time}', '{off_time}')"""
    else:
        query_string = f"""
UPDATE lightschedule
SET hhcode='{hhcode}', lightcode='{lightcode}', monthmatch='{month}', daymatch='{day}', turnon='{on_time}', turnoff='{off_time}'
WHERE id={lightid}"""
    response = "no error"
    try:
        cursor.execute(query_string)
        response = query_string
    except Exception as ex:
        logit(f"failed to execute {query_string} because {ex}")
        response = f"{ex}"
    cursor.close()
    connection.close()
    return response

def delete_light_schedule_detail(lightid):
    """delete one schedule row"""
    response = "no error"
    connection = open_sql_connection()
    cursor = connection.cursor()
    query_string = f"DELETE FROM lightschedule WHERE id = {lightid}"
    try:
        cursor.execute(query_string)
        response = query_string
    except Exception as ex:
        logit(f"failed to execute {query_string} because {ex}")
        response = f"{ex}"
    cursor.close()
    connection.close()
    return response

if __name__ == "__main__":
    print(match_image('219:244:251:218:243:252:221:246:252:220:245:252'))
    print(list_img_folders())
