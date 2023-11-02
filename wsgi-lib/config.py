#!/usr/bin/env python3

# system libraries
import os
import sys
import json

wwwfldr = '/usr/local/www/apache24/'

f = open(wwwfldr + '/cgi-data/config.json')
CONFIG = json.load(f)
f.close()

def config():
    return CONFIG

if __name__ == '__main__':
    print("{}".format(CONFIG['path']))
