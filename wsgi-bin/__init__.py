#!/usr/local/bin/python3

import os
import re
import subprocess
from subprocess import Popen, PIPE
from flask import Flask, g, render_template, Response, request, jsonify
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
import json
from logit import logit

app=Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
wwwfldr = '/usr/local/www/apache24/'
datafldr = wwwfldr + 'cgi-data/'


def parseData(requestdata):
    retval = {}
    for line in requestdata.decode('utf8').split('\n'):
        if line:
            for onepair in line.split('&'):
                if onepair:
                    (key, val) = onepair.split('=')
                    retval[key] = val
    return retval


@app.after_request
def add_header(response):
    response.cache_control.max_age = 0
    return response

@app.route('/')
def index():
    return render_template('index.html',
                           bookmarks=bookmarks.get_bookmarks(),
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
    return devices.get_device_html()

@app.route('/deviceinfo/<the_host>')
def cpuinfo(the_host):
    return jsonify(devices.get_device_info(the_host))

@app.route('/listlight')
def listlight():
    retval = [ 'idx,name,status' ]
    lights = lightctl.get_light_list()
    for key in lights:
        retval.append('{},{},{}'.format(key, lights[key], lightctl.get_light_state(key)))
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
    return Response(retval,mimetype='text/html')

@app.route('/lightsched', methods = ['POST','GET'])
def schedlight():
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        requestobj = request.form
    retval = lightctl.lightsched(requestobj)
    return Response(retval,mimetype='text/html')

@app.route('/getonelightsched/<the_light>', methods = ['GET','POST'])
def getlightsched(the_light):
    retval = lightctl.get_desired_light_states(the_light)
    return Response("\n".join(retval),mimetype='text/tsv')

@app.route('/getlightscheddetail/<the_index>', methods = ['GET', 'POST'])
def getscheddetail(the_index):
    retval = lightctl.get_light_schedule_detail(the_index)
    #logit("/getlightscheddetail/{} {}".format(the_index, retval))
    return jsonify(retval)
   
@app.route('/setlightscheddetail', methods = ['POST'])
def setscheddetail():
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        #logit("request {}".format(request))
        #for subs in request.form:
            #logit("request value {}: {}".format(subs, request.form[subs]))
        requestobj = parseData(request.data)
        #requestobj = request.form
        #logit("requestobj {}".format(requestobj))
        #for key in requestobj:
            #logit("key: " + key + " val: " + requestobj[key]);
    retval = lightctl.set_light_schedule_detail(the_id = requestobj['the_id'],
                                                the_hhcode = requestobj['the_hhcode'],
                                                the_lightcode = requestobj['the_lightcode'],
                                                the_month = requestobj['the_month'],
                                                the_day = requestobj['the_day'],
                                                the_on_time = requestobj['the_on_time'],
                                                the_off_time = requestobj['the_off_time'],
                                                is_new = requestobj['new_item'])
    #logit("/setlightscheddetail/ {}".format(retval))
    return Response(retval,mimetype='text/html')

@app.route('/deletelightscheddetail', methods = ['POST'])
def deletescheddetail():
    retval = 'Undefined'
    requestobj = parseData(request.data)
    retval = lightctl.delete_light_schedule_detail(the_id = requestobj['the_id'])
    #logit("/deletelightscheddetail/ {}".format(retval))
    return Response(retval,mimetype='text/html')

@app.route('/listmixer')
def listmixer():
    retval = ['device,left,right']
    p = re.compile("Mixer ")
    q = re.compile(" *is currently set to *")
    r = re.compile("Recording source:.*")
    s = re.compile(":")
    if os.path.exists('/dev/mixer'):
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
            #logit(output)
        else:
            sep = ""
            for key in request.dir():
                #logit(key)
                #logit(request[key])
                output = "{}{}{}:{}".format(output, sep, key, request[key])
                sep = "\n"
    return Response(output,mimetype='text/html')

#@app.route('/dbtest')
def dbtest():
    retval = ""
    connection = db.open_sql_connection()
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
            #logit("requestobj is {}".format(requestobj))
            if 'COLLAGEQUERY' in requestobj:
                imgid = db.match_image(requestobj['COLLAGEQUERY'])['imgid']
            if 'IMGID' in requestobj:
                imgid = requestobj.get('IMGID')
                if imgid == 'RANDOM':
                    imgid = thumbnail.get_any_imgid()
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
                    retval.append('{},{},{}'.format(outline['fileid'],outline['shortname'],outline['size']))
        except Exception as e:
            print("exception {}".format(e))
    return Response("\n".join(retval),mimetype='text/csv')

@app.route('/getplaylist', methods = ['GET'])
def get_playlist():
    retval = ['fileid,shortname']
    try:
        for outline in music.get_playlist():
            retval.append('{},{}'.format(outline['fileid'],outline['shortname']))
    except Exception as e:
        logit("exception /getplaylist {}".format(e))
    return Response("\n".join(retval),mimetype='text/csv')

@app.route('/addplaylist', methods = ['POST'])
def add_playlist():
    tunename="nothing"
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                fileids = json.loads(requestobj.get('fileid'))
                timestamp = (datetime.datetime.now()).strftime("%s")
                tunename = music.add_playlist(fileids, timestamp)
        except Exception as e:
            logit("exception {}".format(e))
    return Response(tunename,mimetype="text/html")

@app.route('/rmplaylist', methods = ['POST'])
def rm_playlist():
    tunename="nothing"
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                fileids = json.loads(requestobj.get('fileid'))
                tunename = music.rm_playlist(fileids)
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

@app.route('/getweather', methods=['GET','POST'])
def get_weather_data():
    requestobj = {}
    if request.method == 'GET':
        for idx in request.args:
            requestobj[idx] = request.args[idx]
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        if 'start' not in requestobj:
            requestobj['start']=False
        if 'end' not in requestobj:
            requestobj['end']=False
        if 'host' not in requestobj:
            requestobj['host']=False
        if 'pixels' not in requestobj:
            requestobj['pixels']=False
    return Response("\n".join(weather.get_weather_readings(requestobj)),mimetype="text/csv")

@app.route('/saveweather', methods=['POST'])
def save_weather_data():
    if request.method == 'POST':
        requestobj = parseData(request.data)
    if requestobj:
        return jsonify(weather.save_weather_reading(timestamp=requestobj['timestamp'],host=requestobj['host'],reading=requestobj['reading']))
    else:
        raise Exception("request.data: {}".format(request.data))
    raise Exception("WTF man");

@app.route('/getagw', methods=['GET'])
def getheatcolor():
    retval = weather.get_current_vs_historical()
    return jsonify({'status': retval})

@app.route('/getforecast', methods=['GET'])
def getsrqforecast():
    retval = weather.get_forecast(request.remote_addr)
    #logit("{}".format(retval))
    return Response("\n".join(retval),mimetype='text/csv')


@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close()    

if __name__ == '__main__':
  app.run(debug=True)
