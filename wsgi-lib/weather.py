#!/usr/bin/env python3

# system libraries
import json
import urllib.request
from urllib.request import Request
from multiprocessing import Pool

# local libraries here
import db
from config import config
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
            retval.append(f"<span><a href='{weather[next_item]['url']}' title='{weather[next_item]['ttl']}' target=_blank onMouseOver='forecastGraph();'>"
                          f"<svg class='weatherthumb' id='FORECASTGRAPH'></svg></a></span>")
        else:
            retval.append(f"<span><a href='{weather[next_item]['url']}' title='{weather[next_item]['ttl']}' target=_blank><img class='weatherthumb' "
                          f"src='{weather[next_item]['uri']}' alt='{weather[next_item]['alt']}'></a></span>")
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
        where_ts_bound= " WHERE timestamp % 300 = 0 AND "
        where_ts_start=f" timestamp>={start}" if start else ""
        where_ts_and =  " AND" if start and end else ""
        where_ts_end = f" timestamp<={end}" if end else ""
        where_host_and= " AND" if (start or end) and host else ""
        where_host  =  f" host IN ('{host}')" if host else ""
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = "SELECT host, timestamp, reading, AVG(reading) " \
         f" OVER(PARTITION BY host ORDER BY timestamp ROWS BETWEEN {mavg} PRECEDING AND {mavg} FOLLOWING) AS moving_average " \
         f" FROM temperatures{where_ts_bound}{where_ts_start}{where_ts_and}{where_ts_end}{where_host_and}{where_host}"
        if cursor.execute(query):
            for onereading in cursor.fetchall():
                readings.append(f'{onereading[0]},{onereading[1]},{onereading[2]},{onereading[3]}')
        cursor.close()
        connection.close()
    except Exception as ex:
        logit(f"{ex}")
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
            tempval = resultset[1] / resultset[0]
        cursor.close()
        connection.close()
    except Exception as ex:
        logit(f"{ex}")
    redval = 255 if tempval>=1.25 else 0 if tempval <= 1 else (tempval-1)*256*4
    grnval = 255 if tempval<=1.25 else 0 if tempval >= 1.5 else (1.5-tempval)*256*4
    return [redval,grnval]

def save_weather_reading(timestamp = None, host = None, reading = None):
    if timestamp is None or host is None or reading is None:
        raise Exception(f"Cannot use these values - timestamp: {timestamp} host: {host} reading: {reading}")
    try:
        connection = db.open_sql_connection()
        cursor = connection.cursor()
        query = f"INSERT INTO temperatures(timestamp, host, reading) VALUES({timestamp}, '{host}', {reading})"
        if cursor.execute(query):
            cursor.close()
            cursor=connection.cursor()
            query = f"SELECT * FROM temperatures WHERE timestamp={timestamp} AND host='{host}'"
            if cursor.execute(query):
                return cursor.fetchone()
        cursor.close()
        connection.close()
    except Exception as ex:
        logit(f"{ex}")
    # don't know what happened here, hope they can recover
    return None

def get_forecast(ip_address):
    #response = requests.get(f'https://ipapi.co/{ip_address}/json/').json()
    thefinaldata = ["location,timestamp,temperature"]
    for row in db.get_vals_like_key("forecast_data_"):
        for k in row:
            v = json.loads(row[k])
            (p1,p2,location) = k.split('_')
            for dline in v:
                if dline['temperature'] is not None:
                    thefinaldata.append(f"{location},{dline['startTime']},{dline['temperature']}")
    return thefinaldata

def fetch_one_location(bundle):
    thefinaldata=""
    try:
        useragent={'User-Agent':config()['misc']['user-agent']}
        # initial request to get the link to the data
        apireq = Request(f'https://api.weather.gov/points/{bundle[1]}',headers=useragent)
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
        db.set_val_for_key(f'forecast_data_{bundle[0]}', thefinaldata, f'{yr}-{mo}-{dy}')
    except Exception as ex:
        logit(f"{ex}")
    return thefinaldata


if __name__ == '__main__':
    #theapiuris = [["BTR","30.5315,-91.1522" ],
    #              ["NUQ","37.4090,-122.0507"],
    #              ["TCS","32.1145,-110.9392"],
    #              ["DRT","29.6897,-101.1754"],
    #              ["RNO","39.4968,-119.7707"],
    #              ["SRQ","27.3070,-82.4951" ]]
    #db.set_val_for_key('forecast_links',json.dumps(theapiuris))
    theapiuris = json.loads(db.get_val_for_key('forecast_links'))
    with Pool(len(theapiuris)) as p:
        catchval = p.map(fetch_one_location, theapiuris)
