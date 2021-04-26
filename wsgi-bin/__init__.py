#!/usr/local/bin/python3

import os
import re
import subprocess
from subprocess import Popen, PIPE
from flask import Flask, render_template, Response, request, jsonify
import base64
import datetime

import db
import devices
import lightctl
import bookmarks
import weather
import thumbnail
import music
import pix
from logit import logit

app=Flask(__name__)
wwwfldr = '/usr/local/www/apache24/'
datafldr = wwwfldr + 'cgi-data/'


def parseData(requestdata):
    retval = {}
    for line in requestdata.decode('utf8').split('\n'):
        (key, val) = line.split('=')
        logit([key,val])
        retval[key] = val
    return retval


@app.route('/')
def index():
    return render_template('index.html',
                           bookmarks=bookmarks.get_bookmarks(),
                           devices=devices.get_device_html(),
                           weather=weather.get_weather_html(),
                           pix=pix.get_pix_html(),
                           lightsched=lightctl.lightsched(False),
                           music=music.get_music_html())

@app.route('/getimages', methods = ['POST'])
def getimages():
    the_folder_id = -1
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'the_folder_id' in requestobj:
            the_folder_id = requestobj['the_folder_id']
    return jsonify(pix.list_folder(the_folder_id))

@app.route('/getdevices')
def getdevices():
    return jsonify(devices.renderdevices())

@app.route('/deviceinfo/<the_host>')
def cpuinfo(the_host):
    return jsonify(devices.get_device_info(the_host))

@app.route('/listlight')
def listlight():
    retval = [ 'idx,name,status' ]
    lights = lightctl.get_light_list()
    for key in lights:
        retval.append('{},{},{}'.format(key, lights[key], lightctl.get_light_state(key)))
    logit(retval)
    return Response("\n".join(retval),mimetype='text/csv')


@app.route('/getlight')
def getlight():
    retval = 'Undefined'
    requestobj = False
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'DEV' in requestobj:
            thelight = requestobj['DEV']
            retval = "{}:{}".format(thelight, get_light_state(thelight))
        else:
            retval = "Error missing DEV variable"
    else:
        retval = "Error no request found"
    logit(retval)
    return Response(retval,mimetype='text/html')

@app.route('/setlight', methods = ['POST'])
def setlight():
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'DEV' in requestobj and 'STATE' in requestobj:
            retval = lightctl.set_light_state(requestobj['DEV'],
                                              requestobj['STATE'])
        else:
            retval = "Error missing DEV and/or STATE"
    else:
        retval = "Error no request found"
    logit(retval)
    return Response(retval,mimetype='text/html')

@app.route('/lightsched', methods = ['POST','GET'])
def schedlight():
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        logit("request {}".format(request))
        #for subs in request.form:
            #logit("request value {}: {}".format(subs, request.form[subs]))
        requestobj = request.form
        logit("requestobj {}".format(requestobj))
    retval = lightctl.lightsched(requestobj)
    logit("/lightsched {}".format(retval))
    return Response(retval,mimetype='text/html')

@app.route('/listmixer')
def listmixer():
    retval = ['device,left,right']
    p = re.compile("Mixer ")
    q = re.compile(" *is currently set to *")
    r = re.compile("Recording source:.*")
    s = re.compile(":")
    output = Popen(["/usr/sbin/mixer"], stdout=PIPE).communicate()[0]
    for nextdev in output.decode('utf8').split("\n"):
        devname = s.sub(',', r.sub('', q.sub(',', p.sub('', nextdev))))
        if devname:
            retval.append(devname)
    return Response("\n".join(retval),mimetype='text/csv')


@app.route('/getmixer')
def getmixer():
    retval = 'Undefined'
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'DEV' in requestobj:
            mixdev = requestobj['DEV']
            p = re.compile('/Mixer.*is currently set to/')
            output = Popen(["/usr/sbin/mixer", mixdev], stdout=PIPE).communicate()[0]
            retval = output.decode('utf8').split(':')[1]
    return Response(retval,mimetype='text/html')


@app.route('/setmixer', methods = ['POST'])
def setmixer():
    output = 'Undefined'
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'DEV' in requestobj:
            mixdev = requestobj['DEV']
        else:
            mixdev = False
        if 'VALUE' in requestobj:
            mixval = requestobj['VALUE'] * 1
        else:
            mixval = False
        if mixdev and mixval:
            p = re.compile('/Mixer.*is currently set to/')
            output = Popen(["/usr/sbin/mixer",
                            mixdev,
                            '{0}:{0}'.format(mixval)], stdout=PIPE).communicate()[0]
            logit(output)
        else:
            sep = ""
            for key in request.dir():
                logit(key)
                logit(request[key])
                output = "{}{}{}:{}".format(output, sep, key, request[key])
                sep = "\n"
    return Response(output,mimetype='text/html')

@app.route('/dbtest')
def dbtest():
    retval = ""
    connection = db.get_sql_connection()
    tablecursor = connection.cursor()
    if tablecursor.execute("show tables") > 0:
        for nexttable in tablecursor.fetchall():
            nexttablename = nexttable['Tables_in_jupiter']
            retval = "{}<br><br>\nNext table:{}".format(retval,nexttablename)
            detailcursor = connection.cursor()
            if detailcursor.execute("select * from {} limit 10".format(nexttablename)) > 0:
                for nextrow in detailcursor.fetchall():
                    retval = "{}<br>\n{}".format(retval,nextrow)
            detailcursor.close()
    tablecursor.close()
    connection.close()
    return retval

@app.route('/thumbnail', methods = ['GET', 'POST'])
def thumbnail_handler():
    retval = ""
    imgid = False
    size = False
    requestobj = False
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = request.form
    if requestobj:
        try:
            logit("requestobj is {}".format(requestobj))
            if 'COLLAGEQUERY' in requestobj:
                imgid = db.match_image(requestobj['COLLAGEQUERY'])['imgid']
            if 'IMGID' in requestobj:
                imgid = requestobj.get('IMGID')
            if 'SIZE' in requestobj:
                size = requestobj.get('SIZE')
            if 'IMG' in requestobj:
                imgname = requestobj.get('IMG')
                imgid = thumbnail.get_imgid(imgname)
                if not imgid:
                    if os.path.exists(imgname):
                        thumbnail.store_image(imgname,[])
                        imgid = thumbnail.get_imgid(imgname)
                    else:
                        raise ValueError("Not found {}".format(imgname))
        except Exception as e:
            return Response(e,mimetype='text/plain')
    if not imgid:
        imgid = 1
    if not size:
        size  = '64x64'
    retval = thumbnail.get_img_sized(imgid, size)
    return Response(retval,mimetype='image/jpeg')

@app.route('/getmusic', methods = ['GET', 'POST'])
def get_music():
    retval = ['fileid,shortname,size']
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = request.form
    if requestobj:
        try:
            if 'filter' in requestobj:
                tunes = music.get_music_filtered(requestobj.get('filter'))
                for outline in tunes:
                    #outline = tunes[theline]
                    retval.append('{},{},{}'.format(outline['fileid'],outline['shortname'],outline['size']))
        except Exception as e:
            print("exception {}".format(e))
    return Response("\n".join(retval),mimetype='text/csv')
    #return Response("<br/>\n".join(retval),mimetype='text/html')

@app.route('/addplaylist', methods = ['POST'])
def add_playlist():
    tunename="nothing"
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                timestamp = (datetime.datetime.now()).strftime("%s")
                tunename = music.add_playlist(requestobj.get('fileid'), timestamp)
        except Exception as e:
            logit("exception {}".format(e))
    logit("add_playlist: {}".format(tunename))
    return Response(tunename,mimetype="text/html")

@app.route('/rmplaylist', methods = ['POST'])
def rm_playlist():
    tunename="nothing"
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                tunename = music.rm_playlist(requestobj.get('fileid'))
        except Exception as e:
            print("exception {}".format(e))
    logit("rm_playlist: {}".format(tunename))
    return Response(tunename,mimetype="text/html")

@app.route('/nextplaylist', methods=['GET'])
def pop_playlist():
    tunename="nothing"
    try:
        tunename = music.pop_playlist()
    except Exception as e:
        print("exception {}".format(e))
    logit("rm_playlist: {}".format(tunename))
    return Response(tunename,mimetype="text/html")


if __name__ == '__main__':
  app.run(debug=True)
