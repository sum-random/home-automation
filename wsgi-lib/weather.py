#!/usr/bin/env python3

# system libraries
import os
import time

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
                                'alt': 'MIMIC-TPW' } }
    return wlinks


def get_weather_html():
    retval = []
    the_list = get_weather_list()
    for next_item in sorted(the_list):
        retval.append("<span><a href='{}' title='{}' target=_blank><img class='weatherthumb' src='{}' alt='{}'>"
                      "</a></span>".format(the_list[next_item]['url'],
                                           the_list[next_item]['ttl'],
                                           the_list[next_item]['uri'],
                                           the_list[next_item]['alt']))
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
    logit('start: {}  end: {}  host: {}  mavg: {}'.format(start,end,host,mavg))
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
    #logit("save_weather_reading({},{},{})".format(timestamp,host,reading))
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


if __name__ == '__main__':
    the_weather = get_weather_html()
    for the_endpoint in the_weather.split('\n'):
        print(the_endpoint)
