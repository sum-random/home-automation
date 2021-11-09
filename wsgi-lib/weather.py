#!/usr/bin/env python3

# system libraries
import os
import time

# local libraries here
import db
from logit import logit

    
def get_weather_list():
    wlinks = { '4San_Fran_R': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'Tampa radar',
                                'uri': 'https://radblast.wunderground.com/cgi-bin/radar/WUNIDS_map?num=6&amp;type=N0Q&amp;mapx=400&amp;mapy=240&amp;brand=wui&amp;delay=15&amp;frame=0&amp;scale=1&amp;transx=0&amp;transy=0&amp;severe=0&amp;smooth=0&amp;centerx=400&amp;centery=240&amp;station=TBW&amp;rainsnow=0&amp;lightning=0&amp;noclutter=0&amp;showlabels=1&amp;showstorms=0&amp;rand=27272981',
                                'alt': 'Current RADR Tampa FL' },
               '5SoWe_radar': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'SW radar',
                                'uri': 'https://s.w-x.co/staticmaps/wu/wu/wxtype1200_cur/uspie/current.png',
                                'alt': 'St Petersburg FL Regional Radar' },
               '6UnSt_radar': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'US radar',
                                'uri': 'http://icons-ak.wxug.com/data/640x480/2xus_sf_anim.gif',
                                'alt': 'AccuWeather forecast map' },
               '7US_temprtr': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'US temperature',
                                'uri': 'http://icons-ak.wxug.com/data/640x480/2xus_st_anim.gif',
                                'alt': 'Southwest Temperature' },
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
