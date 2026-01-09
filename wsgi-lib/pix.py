#!/usr/bin/env python3

# system libraries
import os
import time
import re

# local libraries here
import db
from logit import logit
from config import config

def get_pix_html():
    retval = []

    retval.append("<h1>Choose a folder to browse</h1>")
    retval.append("<FORM METHOD='POST'>")
    retval.append("<SELECT ID='PICKFOLDER' onChange='populateThumbs();'>")
    folderlist = {}
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = "SELECT fname,imgid FROM thumblist order by 1"
        if cursor.execute(query):
            for imgline in cursor.fetchall():
                dir = os.path.dirname(imgline[0])
                id = imgline[1]
                if not dir in folderlist:
                    folderlist[dir] = {'imgid': id, 'fname': os.path.basename(dir)}
        cursor.close()
        connection.close()
    except Exception as ex:
        folderlist['exception']="{}".format(ex)
    defaultfolder = re.compile('nathan14')
    for folder_name in sorted(folderlist):
        folder = folderlist[folder_name]
        id = folder['imgid']
        name = folder['fname']
        slashes = folder_name.count('/') - 3
        if defaultfolder.search(folder_name):
            selected = "SELECTED "
        else:
            selected = ""
        retval.append("<OPTION {}VALUE='{}'>{}{}</OPTION>".format(selected, id, '-' * slashes, name))
    retval.append("</SELECT>")
    retval.append("<DIV ID='pickathumb' WIDTH='100%' onMouseOver='scrollThumbs();'></DIV>")
    retval.append("<DIV ID='displayimg' WIDTH='100%'></DIV>")
    retval.append("")
    retval.append("</FORM>")

    return '\n'.join(retval)

def list_folder(folder_id):
    imglist = []
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        img_id = folder_id * 1
        query = "SELECT fname,imgid FROM thumblist where imgid={}".format(img_id)
        folder = False
        if cursor.execute(query):
            for imgline in cursor.fetchall():
                file = os.path.basename(imgline[0])
                folder = os.path.dirname(imgline[0])
        cursor.close()
        if folder:
            query = "SELECT fname,imgid FROM thumblist where fname LIKE '{}%'".format(folder)
            cursor = connection.cursor()
            if cursor.execute(query):
                for imgline in cursor.fetchall():
                    imglist.append({'imgid': imgline[1], 'fname': imgline[0]})
            cursor.close()
        connection.close()
    except Exception as ex:
        imglist.append({'exception': "{}".format(ex)})

    return imglist

if __name__ == '__main__':
    html = get_pix_html()
    for endpoint in html.split('\n'):
        print(endpoint)
