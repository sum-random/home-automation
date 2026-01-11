#!/usr/bin/env python3

# system libraries
import os
from subprocess import Popen, PIPE
import datetime
import time
import re
from multiprocessing import Pool

# local libraries here
import db
from logit import logit
from config import config

# Define some consts
CONFIG=config()
LOCKFILE = CONFIG['path']['lockfile']
HOUSECODE = '-c I'

class lockobject():
    _lockfile = False
    def getlock(self):
        while os.access(LOCKFILE, os.F_OK):
            time.sleep(2)
        self._touch(LOCKFILE)
        return True

    def droplock(self):
        if self._lockfile:
            self._lockfile.close()
        if os.access(LOCKFILE, os.F_OK):
            os.unlink(LOCKFILE)
        else:
            return False
        return True
    
    def _touch(self, fname, times=None):
        self._lockfile = open(fname, 'a')

def _shortname(longname):
    return longname.split('.')[0]

    
def get_light_list():
    return db.get_light_list()


def dev_path(light):
    return CONFIG['path']['config'] + 'DEV' + str(light)

def get_light_state(light):
    status = 'Auto'
    devpath = dev_path(light)
    if os.path.exists(devpath):
        f = open(devpath, 'rt')
        status = f.readline()
        f.close()
    return status.strip()


def apply_light_state(light, state):
    mylock = lockobject()
    mylock.getlock()
    cmd = "-{}".format(state[1:2])
    brcmd = [CONFIG['path']['brcmd'], '-x', CONFIG['path']['brdevice'], '-c','I', '-r', '5', cmd, str(light)]
    brout = Popen(brcmd, stdout=PIPE).communicate()
    mylock.droplock()
    return ' '.join(brcmd)


def set_light_state(light, state):
    """ Turn a light on or off
    Record or clear status file
    Acquire a lock
    Set light state
    Drop lock
    
    Args:
    """
    retval = "state {} unchanged {}".format(light, state)
    devpath = dev_path(light)
    if get_light_state(light) != state:
        if state == 'Auto':
            if os.path.exists(devpath):
                os.remove(devpath)
                retval = "state {} changed to Auto".format(light)
        elif state in ['Off', 'On']:
            f = open(devpath, 'w')
            f.write(state)
            f.close()
            retval = apply_light_state(light, state)
        else:
            retval = "Unknown STATE: {}".format(state)
    return retval

def get_desired_light_states(light=-1):
    return db.get_desired_light_states(light)

def get_light_state_ids(light=-1):
    return db.get_light_state_ids(light)
    
def get_light_schedule_detail(id):
    return db.get_light_schedule_detail(id)

def set_light_schedule_detail(id, hhcode, lightcode, month, day, on_time, off_time, is_new):
    return db.set_light_schedule_detail(id, hhcode, lightcode, month, day, on_time, off_time, is_new)

def delete_light_schedule_detail(id):
    return db.delete_light_schedule_detail(id)

def date_match(light_schedule):
    month = False
    day = False
    hour = False
    monthmatch = light_schedule['monthmatch']
    try:
        if monthmatch == '*':
            month = True
        else:
            for monthset in monthmatch.split(','):
                if '-' in monthset:
                    (first, last) = monthset.split('-')
                    if int(first) <= datetime.datetime.now().month and int(last) >= datetime.datetime.now().month:
                        month = True
                else:
                    if int(monthset) == datetime.datetime.now().month:
                        month = True
    except Exception as ex:
        logit("Unable to parse month match {} {}".format(monthmatch, ex))
        month = False
    daymatch = light_schedule['daymatch']
    try:
        if daymatch == '*':
            day = True
        else:
            for dayset in daymatch.split(','):
                if '-' in dayset:
                    (first, last) = dayset.split('-')
                    if int(first) <= datetime.datetime.now().weekday() and int(last) >= datetime.datetime.now().weekday():
                        day = True
                else:
                    if int(dayset) == datetime.datetime.now().weekday():
                        day = True
    except Exception as ex:
        logit("Unable to parse day match {} because {}".format(daymatch, ex))
        day = False
    try:
        curtime = datetime.datetime.now().strftime('%H%M')
        if light_schedule['turnon'] <= curtime and light_schedule['turnoff'] >= curtime:
            hour = True
    except Exception as ex:
        logit("Unable to parse hour match {} {} {}".format(light_schedule['turnon'], light_schedule['turnoff'], ex))
        hour = False
    override = get_light_state(light_schedule['lightcode']) 
    if re.match('Auto',override):
        return month and day and hour
    else:
        return re.match('On',override)

def lightsched(cgi_options):
    retval = []
    monthmatch = '*'
    daymatch = '*'
    turnon = 'HHMM'
    turnoff = 'HHMM'
    pickalight = -1
    if cgi_options:
        if 'PICKALIGHT' in cgi_options:
            pickalight = int(cgi_options['PICKALIGHT'])
        if 'MONTHMATCH' in cgi_options:
            monthmatch = cgi_options['MONTHMATCH']
        if 'DAYMATCH' in cgi_options:
            daymatch = cgi_options['DAYMATCH']
        if 'TURNON' in cgi_options:
            turnon = cgi_options['TURNON']
        if 'TURNOFF' in cgi_options:
            turnoff = cgi_options['TURNOFF']
        if 'MAKENEW' in cgi_options and 'PICKALIGHT' in cgi_options and pickalight > -1:
            valid = True
            if not monthmatchcheck(monthmatch):
                valid = False
                retval.append("{} is not a valid month spec".format(monthmatch))
            nextlight = pickalight
            if valid:
                result = db.set_light_schedule_detail(id=False, hhcode='I', lightcode=nextlight, month=monthmatch, day=daymatch, on_time=turnon, off_time=turnoff, is_new=True)
                retval.append("Added new item to schedule {}<BR>".format(result))
    retval.append("<HR/><FORM METHOD=POST><SELECT NAME='PICKALIGHT' ID='PICKALIGHT' onChange='showOneLightSchedule();'>")
    retval.append("<OPTION VALUE='-1'>Choose a light</OPTION>")
    lights = get_light_list()
    for nextlight in lights:
        selected = ''
        if nextlight == pickalight:
            selected = ' SELECTED'
        retval.append("<OPTION VALUE='{}'{}>{}</OPTION>".format(nextlight, selected,  lights[nextlight]))
    retval.append("</SELECT>")
    retval.append('<DIV STYLE="visibility:hidden;" ID=DIVSCHED>');
    retval.append('<HR/>Schedules<BR>')
    retval.append('<SELECT NAME=SCHEDLIST ID="SCHEDLIST" SIZE=10 onChange="showScheduleItem();"></SELECT>')
    retval.append('<HR/>Modify<BR>')
    retval.append('<TABLE>')
    retval.append('<TR><TH>Month</TH><TD CLASS="borderless"><INPUT TYPE=TEXT ID=MONTHMATCH VALUE={} onChange="showNewButton();"></TD></TR>'.format(monthmatch))
    retval.append('<TR><TH>Day</TH><TD CLASS="borderless"><INPUT TYPE=TEXT ID=DAYMATCH VALUE={} onChange="showNewButton();"></TD></TR>'.format(daymatch))
    retval.append('<TR><TH>Time On</TH><TD CLASS="borderless"><INPUT TYPE=TEXT ID=TURNON VALUE={} onChange="showNewButton();"></TD></TR>'.format(turnon))
    retval.append('<TR><TH>Time Off</TH><TD CLASS="borderless"><INPUT TYPE=TEXT ID=TURNOFF VALUE={} onChange="showNewButton();"></TD></TR>'.format(turnoff))
    retval.append('</TABLE>')
    retval.append('<INPUT TYPE=BUTTON ID="MAKENEW" VALUE=New onClick="submitScheduleUpdate(true)">')
    retval.append('<INPUT TYPE=BUTTON ID="UPDATE" VALUE=Update onClick="submitScheduleUpdate(false)" STYLE="visibility:hidden;">')
    retval.append('<INPUT TYPE=BUTTON ID="DELETE" VALUE=Delete onClick="deleteScheduleItem()" STYLE="visibility:hidden;">')
    retval.append('</DIV>');
    retval.append("</FORM>")
    return '\n'.join(retval)

def next_light_state(light):
    current_state = get_light_state(light)
    new_state = "Off"
    if re.match('Auto', current_state):
        for nextrow in get_light_state_ids(light):
            if date_match(get_light_schedule_detail(nextrow)):
                new_state = "On"
        current_state=new_state
    return current_state

def process_light_schedule(light):
    apply_light_state(light, next_light_state(light))

def check_router():
    do_reset = True
    for check_site in ['1.1.1.1', '8.8.8.8', '9.9.9.9']:
        if os.system("ping -qc 3 " + check_site) == 0:
            do_reset = False
            break
    if do_reset:
        logit("Resetting router")
        apply_light_state(16, 'Off')
        time.sleep(5);
        apply_light_state(16, 'On')

if __name__ == '__main__':
    light_list = get_light_list()
    for light in light_list:
        process_light_schedule(light)
        time.sleep(5)
    check_router()
