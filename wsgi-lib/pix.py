#!/usr/bin/env python3

# system libraries
import os
import time
import re

# local libraries here
import db
from logit import logit

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
                the_dir = os.path.dirname(imgline[0])
                the_id = imgline[1]
                if not the_dir in folderlist:
                    #folderlist[the_dir] = os.path.basename(the_dir)
                    folderlist[the_dir] = {'imgid': the_id, 'fname': os.path.basename(the_dir)}
        cursor.close()
        connection.close()
    except Exception as ex:
        folderlist['exception']="{}".format(ex)
    defaultfolder = re.compile('nathan14')
    for folder_name in sorted(folderlist):
        #logit("folder_name {}".format(folder_name))
        the_folder = folderlist[folder_name]
        #logit("pix.py line 38 the_folder = {}".format(the_folder));
        the_id = the_folder['imgid']
        the_name = the_folder['fname']
        slashes = folder_name.count('/') - 3
        if defaultfolder.search(folder_name):
            selected = "SELECTED "
        else:
            selected = ""
        retval.append("<OPTION {}VALUE='{}'>{}{}</OPTION>".format(selected, the_id, '-' * slashes, the_name))
    retval.append("</SELECT>")
    retval.append("<DIV ID='pickathumb' WIDTH='100%' onMouseOver='scrollThumbs();'></DIV>")
    retval.append("<DIV ID='displayimg' WIDTH='100%'></DIV>")
    retval.append("")
    retval.append("</FORM>")

    return '\n'.join(retval)

def list_folder(the_folder_id):
    imglist = []
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        the_img_id = the_folder_id * 1
        query = "SELECT fname,imgid FROM thumblist where imgid={}".format(the_img_id)
        the_folder = False
        if cursor.execute(query):
            for imgline in cursor.fetchall():
                the_file = os.path.basename(imgline[0])
                the_folder = os.path.dirname(imgline[0])
        cursor.close()
        if the_folder:
            query = "SELECT fname,imgid FROM thumblist where fname LIKE '{}%'".format(the_folder)
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
    the_html = get_pix_html()
    for the_endpoint in the_html.split('\n'):
        print(the_endpoint)
