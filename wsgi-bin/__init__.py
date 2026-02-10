#!/usr/local/bin/python3
"""Flask route definitions for homelab"""

import os
import re
import subprocess
from subprocess import Popen, PIPE
import base64
import datetime
import json

from flask import Flask, g, render_template, Response, request, jsonify

import db
import devices
import lightctl
import bookmarks
import weather
import thumbnail
import music
import pix
from logit import logit
from config import config

app=Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
DATAFLDR = config()['path']['config']


def parse_data(requestdata):
    """parse POST variables"""
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
    """ensure no caching"""
    response.cache_control.max_age = 0
    return response

@app.route('/')
def index():
    """Root page, plus various data pieces"""
    return render_template('index.html',
                           bookmarks=bookmarks.get_bookmarks(),
                           weather=weather.get_weather_html(),
                           pix=pix.get_pix_html(),
                           lightsched=lightctl.lightsched(False),
                           music=music.get_music_html())

@app.route('/getimages', methods = ['POST'])
def getimages():
    """retrieve inage data from database"""
    folder_id = -1
    requestobj=False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        folder_id = requestobj.get('folder_id',-1)
    return jsonify(pix.list_folder(folder_id))

@app.route('/getdevices')
def getdevices():
    """retrieve list of hosts"""
    return devices.get_device_html()

@app.route('/deviceinfo/<host>')
def cpuinfo(host):
    """retrieve information about host"""
    return jsonify(devices.get_device_info(host))

@app.route('/listlight')
def listlight():
    """retrieve list of light names"""
    retval = [ 'idx,name,status' ]
    lights = lightctl.get_light_list()
    for key in lights:
        light_state=lightctl.get_light_state(key)
        retval.append(f"{key},{lights[key]},{light_state}")
    return Response("\n".join(retval),mimetype='text/csv')


@app.route('/getlight')
def getlight():
    """get current light setting"""
    retval = 'Undefined'
    requestobj = False
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        if 'DEV' in requestobj:
            light=requestobj['DEV']
            light_state=lightctl.get_light_state(light)
            retval=f"{light}:{light_state}"
        else:
            retval="Error missing DEV variable"
    else:
        retval="Error no request found"
    return Response(retval,mimetype='text/html')

@app.route('/setlight', methods = ['POST'])
def setlight():
    """override current light schedule, or clear it"""
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
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
    """get all entries for all lights"""
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        requestobj = request.form
    retval = lightctl.lightsched(requestobj)
    return Response(retval,mimetype='text/html')

@app.route('/getonelightsched/<light>', methods = ['GET','POST'])
def getlightsched(light):
    """get all entries for one light"""
    retval = lightctl.get_desired_light_states(light)
    return jsonify(retval)

@app.route('/getlightscheddetail/<index>', methods = ['GET', 'POST'])
def getscheddetail(index):
    """get a single schedule item"""
    retval = lightctl.get_light_schedule_detail(index)
    #logit("/getlightscheddetail/{} {}".format(index, retval))
    return jsonify(retval)

@app.route('/setlightscheddetail', methods = ['POST'])
def setscheddetail():
    """change or create a single schedule item"""
    retval = 'Undefined'
    requestobj = False
    if request.method == 'POST':
        #logit("request {}".format(request))
        #for subs in request.form:
            #logit("request value {}: {}".format(subs, request.form[subs]))
        requestobj = parse_data(request.data)
        #requestobj = request.form
        #logit("requestobj {}".format(requestobj))
        #for key in requestobj:
            #logit("key: " + key + " val: " + requestobj[key]);
    retval = lightctl.set_light_schedule_detail(id = requestobj['id'],
                                                hhcode = requestobj['hhcode'],
                                                lightcode = requestobj['lightcode'],
                                                month = requestobj['month'],
                                                day = requestobj['day'],
                                                on_time = requestobj['on_time'],
                                                off_time = requestobj['off_time'],
                                                is_new = requestobj['new_item'])
    #logit("/setlightscheddetail/ {}".format(retval))
    return Response(retval,mimetype='text/html')

@app.route('/deletelightscheddetail', methods = ['POST'])
def deletescheddetail():
    """delete a single schedule item"""
    retval = 'Undefined'
    requestobj = parse_data(request.data)
    retval = lightctl.delete_light_schedule_detail(id = requestobj['id'])
    return Response(retval,mimetype='text/html')

@app.route('/getlightcurrentstatus/<idx>', methods = ['GET','POST'])
def readonelightcurrentstate(idx):
    """query whether a light should be on or off with current schedule and overrides"""
    retval = lightctl.next_light_state(idx)
    return Response(retval,mimetype='text/html')

@app.route('/listmixer')
def listmixer():
    """parse the list of mixer volume controls"""
    retval = ['device,left,right']
    p = re.compile("Mixer ")
    q = re.compile(" *is currently set to *")
    r = re.compile("Recording source:.*")
    s = re.compile(":")
    if os.path.exists('/dev/mixer'):
        with Popen(["/usr/sbin/mixer"], stdout=PIPE) as pipeline:
            output = pipeline.communicate()[0]
            for nextdev in output.decode('utf8').split("\n"):
                devname = s.sub(',', r.sub('', q.sub(',', p.sub('', nextdev))))
                if devname:
                    retval.append(devname)
    return Response("\n".join(retval),mimetype='text/csv')


@app.route('/getmixer')
def getmixer():
    """get mixer volume items"""
    retval = 'Undefined'
    requestobj=False
    if request.method == 'GET':
        requestobj = request.args
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        if 'DEV' in requestobj:
            mixdev = requestobj['DEV']
            #p = re.compile('/Mixer.*is currently set to/')
            with Popen(["/usr/sbin/mixer", mixdev], stdout=PIPE) as pipeline:
                output = pipeline.communicate()[0]
                retval = output.decode('utf8').split(':')[1]
    return Response(retval,mimetype='text/html')


@app.route('/setmixer', methods = ['POST'])
def setmixer():
    """modify one moxer setting"""
    output = 'Undefined'
    requestobj=False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
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
            #p = re.compile('/Mixer.*is currently set to/')
            with Popen(["/usr/sbin/mixer",
                        mixdev,
                        f'{mixval}:{mixval}'], stdout=PIPE) as pipeline:
                output = pipeline .communicate()[0]
        else:
            sep = ""
            for key in request.dir():
                output = f"{output}{sep}{key}:{request[key]}"
                sep = "\n"
    return Response(output,mimetype='text/html')

@app.route('/thumbnail', methods = ['GET', 'POST'])
def thumbnail_handler():
    """Retrieve a resized image"""
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
                        raise ValueError(f"Not found {imgname}")
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
    """Return list of audio files matching filter"""
    requestobj=False
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
                    retval.append(f"{outline['fileid']},{outline['shortname']},{outline['size']}")
        except Exception as e:
            print(f"exception {e}")
    return Response("\n".join(retval),mimetype='text/csv')

@app.route('/getplaylist', methods = ['GET'])
def get_playlist():
    """retrieve the list of tunes on th eplaylist"""
    retval = ['fileid,shortname']
    try:
        for outline in music.get_playlist():
            retval.append(f"{outline['fileid']},{outline['shortname']}")
    except Exception as e:
        logit(f"exception /getplaylist {e}")
    return Response("\n".join(retval),mimetype='text/csv')

@app.route('/addplaylist', methods = ['POST'])
def add_playlist():
    """add list of items to the playlist"""
    tunename="nothing"
    requestobj=False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                fileids = json.loads(requestobj.get('fileid'))
                timestamp = (datetime.datetime.now()).strftime("%s")
                tunename = music.add_playlist(fileids, timestamp)
        except Exception as e:
            logit(f"exception {e}")
    return Response(tunename,mimetype="text/html")

@app.route('/rmplaylist', methods = ['POST'])
def rm_playlist():
    """remove list of items from the playlist"""
    tunename="nothing"
    requestobj=False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        try:
            if 'fileid' in requestobj:
                fileids = json.loads(requestobj.get('fileid'))
                tunename = music.rm_playlist(fileids)
        except Exception as e:
            print(f"exception {e}")
    logit(f"rm_playlist: {tunename}")
    return Response(tunename,mimetype="text/html")

@app.route('/nextplaylist', methods=['GET'])
def pop_playlist():
    """Retrieve next item from playlist"""
    tunename="nothing"
    try:
        tunename = music.pop_playlist()
    except Exception as e:
        print(f"exception {e}")
    logit(f"rm_playlist: {tunename}")
    return Response(tunename,mimetype="text/html")

@app.route('/getweather', methods=['GET','POST'])
def get_weather_data():
    """Retrieve temperature data"""
    requestobj = {}
    if request.method == 'GET':
        for idx in request.args:
            requestobj[idx] = request.args[idx]
    if request.method == 'POST':
        requestobj = parse_data(request.data)
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
    """Store temperature data"""
    requestobj=False
    if request.method == 'POST':
        requestobj = parse_data(request.data)
    if requestobj:
        return jsonify(weather.save_weather_reading(timestamp=requestobj['timestamp'],
                                                    host=requestobj['host'],
                                                    reading=requestobj['reading']))
    raise RuntimeError(f"request.data: {request.data}")

@app.route('/getagw', methods=['GET'])
def getheatcolor():
    """Get indicator color for graph label"""
    retval = weather.get_current_vs_historical()
    return jsonify({'status': retval})

@app.route('/getforecast', methods=['GET'])
def getforecast():
    """Retrieve cached data for one location"""
    retval = weather.get_forecast()
    #logit("{}".format(retval))
    return Response("\n".join(retval),mimetype='text/csv')


@app.teardown_appcontext
def close_db(error):
    '''Closes the database connection at the end of request.'''    
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == '__main__':
    app.run(debug=True)
