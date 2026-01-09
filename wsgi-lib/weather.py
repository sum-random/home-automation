#!/usr/bin/env python3

# system libraries
import os,time,json
import urllib.request
import urllib.request,http.client
from urllib.request import Request
import requests
from multiprocessing import Pool
import datetime

# local libraries here
import db
from logit import logit

    
def get_weather_list():
    wlinks = { 
               '5SoWe_radar': { 'url': 'https://www.wunderground.com/weather/us/fl/sarasota/KFLSARAS2114',
                                'ttl': 'Local radar',
                                'uri': 'https://s.w-x.co/staticmaps/wu/wu/wxtype1200_cur/uspie/animate.png',
                                'alt': 'St Petersburg FL Regional Radar' },
               '8Prec_fcast': { 'url': 'http://wxmaps.org/pix/clim.html',
                                'ttl': 'Precipitation forecast',
                                'uri': 'http://wxmaps.org/pix/prec1.png',
                                'alt': 'Precipitation forecast' },
               '9Mimic_tpw':  { 'url': 'http://tropic.ssec.wisc.edu/real-time/mtpw2',
                                'ttl': 'MIMIC-TPW',
                                'uri': 'http://tropic.ssec.wisc.edu/real-time/mtpw2/webAnims/tpw_nrl_colors/global2/mimictpw_global2_latest.gif',
                                'alt': 'MIMIC-TPW' },
               'forecast':    { 'url': '/getforecast',
                                'ttl': 'SRQ FL Forecast',
                                'uri': 'https://api.weather.gov/points/27.307,-82.4951',
                                'alt': 'SRQ FL Forecast' } }
    return wlinks


def get_weather_html():
    retval = []
    weather = get_weather_list()
    for next_item in sorted(weather):
        if weather[next_item]['url'] == '/getforecast':
            retval.append("<span><a href='{}' title='{}' target=_blank onMouseOver='forecastGraph();'><svg class='weatherthumb' id='FORECASTGRAPH'></SVG>"
                          "</a></span>".format(weather[next_item]['url'],
                                               weather[next_item]['ttl']))
        else:
            retval.append("<span><a href='{}' title='{}' target=_blank><img class='weatherthumb' src='{}' alt='{}'>"
                          "</a></span>".format(weather[next_item]['url'],
                                               weather[next_item]['ttl'],
                                               weather[next_item]['uri'],
                                               weather[next_item]['alt']))
    retval.append('<script type="text/javascript">')
    retval.append('    setupWeather();')
    retval.append('</script>')
    return '\n'.join(retval)

def get_weather_readings(request): 
    start=int(request['start']) if request['start'] else db.get_first_time(request['host'])
    end=int(request['end']) if request['end'] else db.get_last_time(request['host'])
    host=request['host']
    pixels=int(request['pixels'])
    mavg = 2 if not (pixels and end and start) else int((end-start)/300/pixels)+1
    readings=['host,timestamp,reading,mavg']
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = "SELECT id, timestamp, host, reading, AVG(reading) " \
         " OVER(PARTITION BY host ORDER BY timestamp ROWS BETWEEN {} PRECEDING AND {} FOLLOWING) AS moving_average " \
         " FROM temperatures{}{}{}{}{}{}".format(mavg,mavg, \
         " WHERE timestamp % 300 = 0 AND ", \
         " timestamp>={}".format(start) if start else "", \
         " AND" if start and end else "", \
         " timestamp<={}".format(end) if end else "", \
         " AND" if (start or end) and host else "", \
         " host IN ('{}')".format(host) if host else "")
        if cursor.execute(query):
            for onereading in cursor.fetchall():
                readings.append("{},{},{},{}".format(onereading[2],onereading[1],onereading[3],onereading[4]))
        cursor.close()
        connection.close()
    except Exception as ex:
        logit("{}".format(ex))
    return readings

# compare current average to average of all measurements
def get_current_vs_historical():
    tempval = 1
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = "select b.alltime, a.current from (select 1 as one,avg(reading) as alltime from temperatures where timestamp%300=0) b INNER JOIN (select 1 as one, avg(reading) as current from temperatures where timestamp=(select max(timestamp) from temperatures where timestamp%300=0)) a ON a.one=b.one;"
        #select b.alltime, a.current from (select 1 as one,avg(reading) as alltime from temperatures) b INNER JOIN (select 1 as one, avg(reading) as current from temperatures where timestamp=(select max(timestamp) from temperatures)) a ON a.one=b.one;"
        if cursor.execute(query):
            resultset = cursor.fetchone()
            tempval = resultset[1] / resultset[0];
        cursor.close()
        connection.close()
    except Exception as ex:
        logit("{}".format(ex))
    redval = 255 if tempval>=1.25 else 0 if tempval <= 1 else (tempval-1)*256*4
    grnval = 255 if tempval<=1.25 else 0 if tempval >= 1.5 else (1.5-tempval)*256*4
    return [redval,grnval]

def save_weather_reading(timestamp = None, host = None, reading = None):
    if timestamp is None or host is None or reading is None:
        raise Exception("Cannot use these values - timestamp: {} host: {} reading: {}".format(timestamp, host, reading))
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = "INSERT INTO temperatures(timestamp, host, reading) VALUES({}, '{}', {})".format(timestamp, host, reading)
        if cursor.execute(query):
            cursor.close()
            cursor=connection.cursor()
            query = "SELECT * FROM temperatures WHERE timestamp={} AND host='{}'".format(timestamp,host)
            if cursor.execute(query):
                return cursor.fetchone()
        cursor.close()
        connection.close()
    except Exception as ex:
        logit("{}".format(ex))
    # don't know what happened here, hope they can recover
    return None

def get_forecast(ip_address):
    #response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    thefinaldata = ["location,time,temperature"]
    for row in db.get_vals_like_key("forecast_data_"):
        for k in row:
            v = json.loads(row[k])
            (p1,p2,location) = k.split('_')
            for dline in v:
                thefinaldata.append("{},{},{}".format(location,dline['startTime'],dline['temperature']))
    return thefinaldata

def fetch_one_location(bundle):
    thefinaldata=""
    try:
      useragent={'User-Agent':'household services host, clayton.69.tucker@gmail.com'}
      # initial request to get the link to the data
      apireq = Request('https://api.weather.gov/points/{}'.format(bundle[1]),headers=useragent)
      req = urllib.request.urlopen(apireq)
      theapidata = json.loads(req.read())
      # now fetch the forecast data
      uri=theapidata['properties']['forecastHourly']
      apireq = Request(uri,headers=useragent)
      req = urllib.request.urlopen(apireq)
      theapidata = json.loads(req.read())
      #db.set_val_for_key('one_raw_forecast',json.dumps(theapidata))
      thefinaldata = json.dumps(theapidata['properties']['periods'])
      (yr,mo,dy,tz) = theapidata['properties']['periods'][0]['startTime'].split('-')
      db.set_val_for_key("forecast_data_{}".format(bundle[0]), thefinaldata, '{}-{}-{}'.format(yr,mo,dy))
    except Exception as ex:
      logit("{}".format(ex))
    return thefinaldata


if __name__ == '__main__':
    theapiuris = [["BTR","30.5315,-91.1522" ],
                  ["NUQ","37.4090,-122.0507"],
                  ["TCS","32.1145,-110.9392"],
                  ["DRT","29.6897,-101.1754"],
                  ["RNO","39.4968,-119.7707"],
                  ["SRQ","27.3070,-82.4951" ]]
    db.set_val_for_key('forecast_links',json.dumps(theapiuris))
    theapiuris = json.loads(db.get_val_for_key('forecast_links'))
    p = Pool(len(theapiuris))
    retval = p.map(fetch_one_location, theapiuris)
    p.close()
    p.join()
    #print("{}".format(get_forecast('10.4.69.64')))
