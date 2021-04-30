#!/usr/bin/env python3

import re
import os
import subprocess
from subprocess import Popen, PIPE
from multiprocessing import Pool
import socket
import json
import syslog
import time
import pymysql
from urllib.parse import unquote_plus

# local libraries
import db
from logit import logit

# Define some consts
MPG123BIN="/usr/local/bin/mpg123"

def get_music_html():
    retval = []

    retval.append("<h1>Search by title</h1>")
    retval.append("<span><input id='TUNEFILTER' name='TUNEFILTER' type='text' onkeyup='populateMusicList()'></span>")
    retval.append("<h1>Search results</h1>")
    retval.append("<select id='TUNELIST' name='TUNELIST' multiple></select>")
    retval.append("<br/>")
    retval.append("<img src='/img/btn_lt.jpg' onclick='rmtunes();' alt='remove from play list'>&nbsp;")
    retval.append("<img src='/img/btn_rt.jpg' onclick='addtunes();' alt='add to play list'><br/>")

    return '\n'.join(retval)

def get_music_filtered(filter):
    connection = db.get_sql_connection()
    retval = []
    for subfilter in filter.split('|'):
        if len(subfilter) > 2:
            cursor = connection.cursor()
            query = ("SELECT fileid,shortname,size FROM musicfiles "
                     "WHERE filename LIKE '%{}%' "
                     "ORDER BY shortname".format(subfilter.replace(' ','%')))
            if cursor.execute(query):
                for musicline in cursor.fetchall():
                    retval.append({'fileid': musicline[0], 'shortname': musicline[1], 'size': musicline[2]})
        cursor.close()
    connection.close()
    return sorted(retval,key=lambda k: k['shortname'])

def get_playlist(randomize=False):
    retval = []
    try:
        connection = db.get_sql_connection()
        if randomize:
            randclause = "pl.timestamp+RAND() AS ordering"
        else:
            randclause = "mf.shortname as ordering"
        cursor = connection.cursor()
        query = ("SELECT mf.fileid, mf.shortname, {}, mf.filename "
                 "FROM musicfiles mf "
                 "INNER JOIN playlist pl ON pl.fileid=mf.fileid "
                 "ORDER BY 3,2".format(randclause))
        if cursor.execute(query):
            for row in cursor.fetchall():
                filename = unquote_plus(row['filename']).decode('utf8')
                retval.append({'fileid': row['fileid'], 'shortname': row['shortname'], 'filename': filename})
        cursor.close()
    except pymysql.err.IntegrityError as ie:
        print(ie)
    return retval

def pop_playlist():
    retval = []
    try:
        connection = db.get_sql_connection()
        cursor = connection.cursor()
        query = ("SELECT mf.fileid, mf.filename, pl.timestamp+RAND() AS ordering "
                 "FROM musicfiles mf "
                 "INNER JOIN playlist pl ON pl.fileid=mf.fileid "
                 "ORDER BY 3,2 LIMIT 1")
        if cursor.execute(query):
            for row in cursor.fetchall():
                filename = unquote_plus(row['filename']).decode('utf8')
                retval.append("/storage/{}".format(filename))
                rm_playlist(row['fileid'])
        cursor.close()
        connection.close()
    except pymysql.err.IntegrityError as ie:
        print(ie)
    return '\n'.join(retval)

def add_playlist(fileid,timestamp=0):
    retval = []
    try:
        connection = db.get_sql_connection()
        cursor = connection.cursor()
        query=("SELECT mf.fileid, pl.fileid AS existing, mf.shortname "
               "FROM musicfiles mf "
               "LEFT JOIN playlist pl ON mf.fileid=pl.fileid "
               "WHERE mf.fileid={}".format(fileid))
        if cursor.execute(query):
            for musicline in cursor.fetchall():
                if not musicline['existing']:
                    logit("add_playlist.musicline: {}".format(musicline))
                    retval.append(musicline['shortname'])
                    inserter = connection.cursor()
                    query = ("INSERT INTO playlist(fileid,timestamp) "
                             "VALUES({},{})".format(fileid,timestamp))
                    logit(query)
                    inserter.execute(query)
                    #inserter.commit()
                    inserter.close()
                else:
                    logit("add_playlist.not_adding: {}".format(musicline))
        cursor.close()
        connection.close()
    except pymysql.err.IntegrityError as ie:
        print(ie)

    return '\n'.join(retval)

def rm_playlist(fileid):
    retval = []
    try:
        connection = db.get_sql_connection()
        cursor = connection.cursor()
        query=("SELECT mf.fileid, mf.shortname "
               "FROM musicfiles mf "
               "INNER JOIN playlist pl ON pl.fileid=mf.fileid "
               "WHERE mf.fileid={}".format(fileid))
        if cursor.execute(query):
            for musicline in cursor.fetchall():
                retval.append(musicline['shortname'])
                remover = connection.cursor()
                query = "DELETE FROM playlist WHERE fileid={}".format(musicline['fileid'])
                logit(query)
                remover.execute(query)
                #remover.commit()
                remover.close()
        cursor.close()
        connection.close()
    except pymysql.err.IntegrityError as ie:
        print(ie)

    return '\n'.join(retval)


if __name__ == '__main__':
    connection = db.get_sql_connection()

    print(get_music_html())

    print(get_music_filtered('skinny'))

    for tune in get_music_filtered('slayer raining'):
        print("  adding: {}".format(add_playlist(tune['fileid'])))

    for tune in get_playlist(False):
        print(" showing: {}".format(tune))

    for tune in get_playlist(True):
        print("removing: {}".format(rm_playlist(tune['fileid'])))
    connection.close()
