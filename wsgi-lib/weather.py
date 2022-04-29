#!/usr/bin/env python3

# system libraries
import os
import time

# local libraries here
import db
from logit import logit

    
def get_weather_list():
    wlinks = { 
               '5SoWe_radar': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'SW radar',
                                'uri': 'https://s.w-x.co/staticmaps/wu/wu/wxtype1200_cur/uspie/current.png',
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


if __name__ == '__main__':
    the_weather = get_weather_html()
    for the_endpoint in the_weather.split('\n'):
        print(the_endpoint)
