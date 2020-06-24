#!/usr/bin/env python3

# system libraries
import os
import time

# local libraries here
import db
from logit import logit

    
def get_weather_list():
    wlinks = { '1EPAC_Vapor': { 'url': 'http://www.nrlmry.navy.mil/sat-bin/epac_westcoast.cgi',
                                'ttl': 'EPAC Vapor',
                                'uri': 'http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/vapor/LATEST.jpg',
                                'alt': 'Water vapor image' },
               '2Rain_rate':  { 'url': 'http://www.nrlmry.navy.mil/sat-bin/display10.cgi?PHOT=yes&CURRENT=LATEST.jpg&NAV=rain&AREA=pacific/eastern/pacus/ir_color',
                                'ttl': 'EPAC ir_color',
                                'uri': 'http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/ir_color/LATEST.jpg',
                                'alt': 'Rain rate' },
               '3Montry_vis': { 'url': 'http://www.nrlmry.navy.mil/sat-bin/epac_westcoast.cgi',
                                'ttl': 'Monterey visible',
                                'uri': 'http://www.nrlmry.navy.mil/archdat/pacific/eastern/monterey_bay/vis/LATEST.jpg',
                                'alt': 'Visible' },
               '4San_Fran_R': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'San Francisco radar',
                                'uri': 'https://radblast.wunderground.com/cgi-bin/radar/WUNIDS_map?station=MUX&brand=wui&num=6&delay=15&type=N0R&frame=0&scale=1.000&noclutter=0&showstorms=0&mapx=400&mapy=240&centerx=400&centery=240&transx=0&transy=0&showlabels=1&severe=0&rainsnow=0&lightning=0&smooth=0&rand=24768313&lat=0&lon=0&label=you',
                                'alt': 'Current RADR San Francisco CA' },
               '5SoWe_radar': { 'url': 'http://www.wunderground.com/',
                                'ttl': 'SW radar',
                                'uri': 'https://s.w-x.co/staticmaps/wu/wu/wxtype1200_cur/usrno/current.png',
                                'alt': 'Reno NV Regional Radar' },
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
