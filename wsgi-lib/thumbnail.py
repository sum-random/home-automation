#!/usr/bin/env python3

# system libraries
import os
import re
import time
import flask
import base64
import io
from PIL import Image, ExifTags
from multiprocessing import Pool, cpu_count, Lock


# local libraries here
import db
from logit import logit

write_lock = Lock()

def get_img_sized(imgid, size):
    """ Return an Image in the requested size """
    connection = db.get_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT fname FROM thumblist WHERE imgid={};".format(imgid)):
        cursor.close()
        fname = cursor.fetchone()['fname']
        # logit("{} {}".format(fname, size))
        if size == 'FULL':
            return open(fname, 'rb').read()
        cursor = connection.cursor()
        if cursor.execute("SELECT imgdata FROM imgcache WHERE imgid={} AND size='{}'".format(imgid, size)):
            return base64.b64decode(cursor.fetchone()['imgdata'])
        else:
            store_image(fname, [size])
            return get_img_sized(imgid, size)
    else:
        return False
 
def get_exif_dict(image):
    """ Return exif data in a dict """
    retval = {}
    try:
        exif = image._getexif()
        if exif:
            for key in exif:
                retval[ExifTags.TAGS[key]] = exif[key]
    except Exception as ex:
        logit("get_exif_dict() failure: {}".format(ex))
    return retval


def auto_rotate(image):
    """ rotate camera images """
    exdict = get_exif_dict(image)
    if 'Orientation' in exdict:
        angle = False
        if exdict['Orientation'] == 3:
            angle = 180
        if exdict['Orientation'] == 6:
            angle = 270
        if exdict['Orientation'] == 8:
            angle = 90
        if angle:
            logit("rotating {}".format(angle))
            image = image.rotate(angle, expand=True)
    return image


def get_imgid(img_path):
    connection = db.get_sql_connection()
    cursor = connection.cursor()
    if cursor.execute("SELECT imgid FROM thumblist WHERE fname='{}';".format(img_path)):
        imgid = cursor.fetchone()['imgid']
        # logit("found imgid: {}".format(imgid))
    else:
        logit("not in db: {}".format(img_path))
        imgid = False
    cursor.close()
    return imgid


def clean_image(img_path):
    """ remove an entry for a deleted image file """
    imgid = get_imgid(img_path)
    connection = db.get_sql_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM imgcache WHERE imgid = {0};"
                   "DELETE FROM thumblist WHERE imgid = {0};".format(imgid))
    cursor.close()
    connection.commit()
      

def store_image(img_path, sizes=[ '16x16',
                                  '24x24',
                                  '32x32',
                                  '480',
                                  '64',
                                  '64x64' ]):
    """ Load image from disk and store in db resized per the sizes list """
    connection = db.get_sql_connection()
    im = False
    if re.search('/jpg|jpeg/', img_path):
        exif = get_exif_dict(Image.open(img_path))
    else:
        exif={}
    if 'Model' in exif:
        keylist = ""
        for keys in exif:
            keylist = "{} {}".format(keylist, keys)
        logit("{}: {}\n{}".format(img_path, exif['Model'], keylist))
    imgid = get_imgid(img_path)
    retval = []
    if not imgid and os.path.exists(img_path):
        try:
            logit("attempt to open {}".format(img_path))
            im = auto_rotate(Image.open(img_path))
            im_copy = im.copy()
            im_copy = im_copy.resize((2,2), resample=Image.LANCZOS)
            print(im_copy.format, im_copy.size, im_copy.mode)
            (ur,ul,lr,ll) = im_copy.getdata()
            sql = ("INSERT INTO thumblist(fname, urr, urg, urb, ulr, ulg, ulb, lrr, lrg, lrb, llr, llg, llb) "
                   "VALUES('{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})"
                   "".format(img_path, ur[0], ur[1], ur[2], ul[0], ul[1], ul[2], lr[0], lr[1], lr[2], ll[0], ll[1], ll[2]))
            write_lock.acquire()
            logit("{} lock acquired for connection {}".format(write_lock, connection))
            logit(sql)
            connection = db.get_sql_connection(True)
            cursor = connection.cursor()
            if cursor.execute(sql) > 0:
                connection.commit()
                cursor.close()
                cursor = connection.cursor()
                if cursor.execute("SELECT imgid FROM thumblist WHERE fname='{}';".format(img_path)):
                    imgid = cursor.fetchone()['imgid']
            cursor.close()
            write_lock.release()
            logit("{} lock released".format(write_lock))
        except Exception as e:
            logit("failed to insert {} because exception {}".format(img_path, e))
    elif not imgid:
        logit("Cannot open {}".format(img_path))
    
    if imgid:
        for next_size in sizes:
            connection = db.get_sql_connection()
            cursor = connection.cursor()
            if not cursor.execute("SELECT imgdatalen FROM imgcache WHERE imgid={} AND size='{}'".format(imgid, next_size)):
                cursor.close()
                logit("{} imgid {} size {} missing".format(img_path, imgid, next_size))
                if not im:
                    im = auto_rotate(Image.open(img_path))
                if 'x' in next_size:
                    (width, height) = next_size.split('x')
                else:
                    (imwd, imht) = im.size
                    if imwd > imht:
                        width = next_size
                        height = imht * int(next_size) / imwd
                    else:
                        height = next_size
                        width = imwd * int(next_size) / imht
                logit("resize {} {}".format(width, height))
                im_copy = im.resize((int(width), int(height)), resample=Image.LANCZOS)
                stringbuffer = io.BytesIO()
                im_copy.save(stringbuffer, 'jpeg')
                sql = ("INSERT INTO imgcache (imgid, size, imgdata) "
                       "VALUES ({}, '{}', '{}')"
                       "".format(imgid, next_size, base64.b64encode(stringbuffer.getvalue())))
                logit("would like to lock now {}".format(imgid))
                retval.append(sql)
                write_lock.acquire()
                logit("{} write lock acquired for {}".format(write_lock, connection))
                logit(sql[:100])
                try:
                    cursor.close()
                    #w_connection = db.get_sql_connection(True)
                    #logit("my new connection {}".format(w_connection))
                    cursor = connection.cursor()
                    if cursor.execute(sql, (imgid, next_size, base64.b64encode(stringbuffer.getvalue()))):
                        cursor.close()
                        connection.commit()
                        #w_connection.close()
                        logit("success")
                    #else:
                    #    logit("cannot save {} imgid {} size {}".format(img_path, imgid, next_size))
                except Exception as oops:
                    logit('{}'.format(oops))
                write_lock.release()
                logit("{} lock released".format(write_lock))
            else:
                # logit("{} imgid {} size {} present {} bytes".format(img_path, imgid, next_size, cursor.fetchone()['imgdatalen']))
                cursor.close()
    return '\n'.join(retval)


def check_folder(expr, dirname, names):
    work = []
    for fname in names:
        if expr.search(fname):
            work.append(os.path.join(dirname,fname))
            #store_image(os.path.join(dirname,fname))
    pool.map(store_image, work)
    
    


if __name__ == '__main__':
    """ main functionality is to scan filesystem and database and to throw out deleted files and read new file data into db """
    connection = db.get_sql_connection()
    cursor = connection.cursor()
    logit("fixup incomplete thumbs")
    if cursor.execute("SELECT imgid, fname, llb FROM thumblist"):
        for nextrow in cursor.fetchall():
            if os.path.isfile(nextrow['fname']):
                if nextrow['llb'] == -1:
                    logit("fix thumb {}".format(nextrow['fname']))
                    store_image(nextrow['fname'])
            else:
                logit("file removed {}".format(nextrow['fname']))
                clean_image(nextrow['fname'])
        for (dirpath, dirnames, filenames) in os.walk('/storage/Image'):
            for nextfile in filenames:
                if re.search(u'jpg$|jpeg$|png$|tiff$|ico$', nextfile):
                    filepath = os.path.join(dirpath, nextfile)
                    imgid = get_imgid(filepath)
                    if not imgid:
                        logit("store image {}".format(filepath))
                        store_image(filepath)

