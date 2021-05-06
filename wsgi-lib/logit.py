#!/usr/bin/env python3

# system libraries
import os
import sys
from subprocess import Popen, PIPE
import datetime
import time
import multiprocessing
import syslog


wwwfldr = '/usr/local/www/apache24/'
datafldr = wwwfldr + 'cgi-data/'

def logit(loglines):
    thepid = multiprocessing.current_process().pid
    thename = multiprocessing.current_process().name
    thelogfile = open(datafldr + "flask.log", 'a')
    syslog.openlog()
    if isinstance(loglines, str):
        loglines = [loglines]
    for nextlog in loglines:
        for nextline in str(nextlog).split("\n"):
            print(nextline,file=sys.stderr)
            syslog.syslog(nextline)
            timestamp = datetime.datetime.now()
            thelogfile.write("{} {} [{}]: {}\n".format(timestamp.isoformat(), thename, thepid, nextline))
            thelogfile.flush()
            time.sleep(0.001)
    thelogfile.close()
    syslog.closelog()



if __name__ == '__main__':
    logit("this is one line")
    logit(["this is the first line of two", "this is the second\nline of two"])
