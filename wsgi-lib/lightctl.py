#!/usr/bin/env python3

# system libraries
import os
from subprocess import Popen, PIPE
import time

# local libraries here
import db
from logit import logit

# Define some consts
LOCKFILE = "/tmp/br.lock"
HOUSECODE = '-c I'
BRCMD = '/usr/local/bin/br'


def _getlock():
    while os.access(LOCKFILE, os.F_OK):
        logit("I sleep for the lock")
        time.sleep(2)
    _touch(LOCKFILE)
    logit("I have the lock")
    return True

def _droplock():
    if os.access(LOCKFILE, os.F_OK):
        os.unlink(LOCKFILE)
        logit("I release the lock")
    else:
        logit("Strange, {} not present".format(LOCKFILE))
        return False
    return True
    
def _touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)

def _shortname(longname):
    return longname.split('.')[0]

    
def get_light_list():
    lights = { 1: 'Computer',
               2: 'Sofa right',
               3: 'Shoes',
               4: 'Entryway',
               5: 'Television',
               6: 'Sofa left',
               10: 'Buffet Left',
               12: 'Buffet Right',
               14: 'Nathans computer' }
    return lights


def dev_path(the_light):
    APACHE="/usr/local/www/apache24"
    CGIDATA="{}/cgi-data/".format(APACHE)
    return CGIDATA + 'DEV' + str(the_light)

def get_light_state(the_light):
    status = 'Auto'
    devpath = dev_path(the_light)
    if os.path.exists(devpath):
        f = open(devpath, 'rb')
        status = f.readline()
        f.close()
    return status.strip()


def apply_light_state(the_light, the_state):
    _getlock()
    cmd = "-{}".format(the_state[1:2])
    brcmd = [BRCMD, '-x', '/dev/cuau0', '-c','I', '-r', '5', cmd, the_light]
    brout = Popen(brcmd, stdout=PIPE).communicate()
    if brout[0]:
        logit(brout[0])
    _droplock()
    return ' '.join(brcmd)


def set_light_state(the_light, the_state):
    """ Turn a light on or off
    Record or clear status file
    Acquire a lock
    Set light state
    Drop lock
    
    Args:
    """
    retval = "state {} unchanged {}".format(the_light, the_state)
    devpath = dev_path(the_light)
    if get_light_state(the_light) != the_state:
        if the_state == 'Auto':
            if os.path.exists(devpath):
                os.remove(devpath)
                retval = "state {} changed to Auto".format(the_light)
        elif the_state in ['Off', 'On']:
            f = open(devpath, 'w')
            f.write(the_state)
            f.close()
            retval = apply_light_state(the_light, the_state)
        else:
            retval = "Unknown STATE: {}".format(the_state)
    return retval

def get_desired_light_states():
    connection = db.get_sql_connection()
    cursor = connection.cursor()
    logit("read light schedule from database")
    if cursor.execute("SELECT hhcode, lightcode, monthmatch, daymatch, turnon, turnoff FROM lightschedule"):
        for nextrow in cursor.fetchall():
            logit("light state row: {}".format(nextrow))
            if nextrow['monthmatch'] is not none:
                pass
            else:
                monthvalid = True


if __name__ == '__main__':
    for the_light in get_light_list():
        logit("Light {} state {}".format(the_light, get_light_state(the_light)))
    get_desired_light_states()
