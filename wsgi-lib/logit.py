#!/usr/bin/env python3

# system libraries
import os
import sys
from subprocess import Popen, PIPE
import datetime
import time
import multiprocessing

# local packages
from config import config

def logit(loglines):
    thepid = multiprocessing.current_process().pid
    thename = multiprocessing.current_process().name
    thelogfile = open(config()['path']['config'] + "flask.log", 'a')
    if isinstance(loglines, str):
        loglines = [loglines]
    for nextlog in loglines:
        for nextline in str(nextlog).split("\n"):
            print(nextline,file=sys.stderr)
            timestamp = datetime.datetime.now()
            thelogfile.write("{} {} [{}]: {}\n".format(timestamp.isoformat(), thename, thepid, nextline.encode('unicode-escape').decode('ascii')))
            thelogfile.flush()
            time.sleep(0.001)
    thelogfile.close()



if __name__ == '__main__':
    logit("this is one line")
    logit(["this is the first line of two", "this is the second\nline of two"])
