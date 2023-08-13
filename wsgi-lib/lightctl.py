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

# Define some consts
LOCKFILE = "/tmp/br.lock"
HOUSECODE = '-c I'
BRCMD = '/usr/local/bin/br'

class lockobject():
    _lockfile = False
    def getlock(self):
        while os.access(LOCKFILE, os.F_OK):
            #logit("I sleep for the lock")
            time.sleep(2)
        self._touch(LOCKFILE)
        #logit("I have the lock")
        return True

    def droplock(self):
        if self._lockfile:
            self._lockfile.close()
        if os.access(LOCKFILE, os.F_OK):
            os.unlink(LOCKFILE)
            #logit("I release the lock")
        else:
            #logit("Strange, {} not present".format(LOCKFILE))
            return False
        return True
    
    def _touch(self, fname, times=None):
        self._lockfile = open(fname, 'a')
        #os.utime(fname, times)

def _shortname(longname):
    return longname.split('.')[0]

    
def get_light_list():
    lights = { 1: 'Bedroom',
               2: 'Living room L',
               3: 'Living room R',
               4: 'Sofa',
               5: 'Freezer',
               6: 'Salt rock',
               9: 'Sun room',
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
        f = open(devpath, 'rt')
        status = f.readline()
        f.close()
    #logit("light {} status {}".format(the_light, status))
    return status.strip()


def apply_light_state(the_light, the_state):
    mylock = lockobject()
    mylock.getlock()
    cmd = "-{}".format(the_state[1:2])
    brcmd = [BRCMD, '-x', '/dev/cuau1', '-c','I', '-r', '5', cmd, str(the_light)]
    #logit("brcmd {}".format(brcmd))
    brout = Popen(brcmd, stdout=PIPE).communicate()
    #if brout[0]:
        #logit(brout[0])
    mylock.droplock()
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

def get_desired_light_states(the_light):
    retval = ['id\tdescr']
    connection = db.open_sql_connection()
    cursor = connection.cursor()
    #logit("read light schedule from database")
    if the_light == -1:
        where = '' #  all light codes
    else:
        where = " WHERE lightcode={}".format(the_light)
    if cursor.execute("SELECT id, lightcode, monthmatch, daymatch, turnon, turnoff, hhcode FROM lightschedule{}".format(where)):
        for nextrow in cursor.fetchall():
            #logit("light state row: {}".format(nextrow))
            retval.append("{}\tHousecode: {} Month: {} Day: {} Turn On: {} Turn Off: {}".format(nextrow[0], nextrow[6], nextrow[2], nextrow[3], nextrow[4], nextrow[5]))
    cursor.close()
    connection.close()
    return retval

def get_light_state_ids(the_light):
    retval = []
    connection = db.open_sql_connection()
    cursor = connection.cursor()
    #logit("read light schedule from database")
    if the_light == -1:
        where = '' #  all light codes
    else:
        where = " WHERE lightcode={}".format(the_light)
    if cursor.execute("SELECT id FROM lightschedule{}".format(where)):
        for nextrow in cursor.fetchall():
            retval.append(nextrow[0])
    cursor.close()
    connection.close()
    return retval
    
def get_light_schedule_detail(the_id):
    retval = {}
    connection = db.open_sql_connection()
    cursor = connection.cursor()
    #logit("get_light_schedule_detail({})".format(the_id))
    if cursor.execute("SELECT id, lightcode, monthmatch, daymatch, turnon, turnoff, hhcode FROM lightschedule WHERE id={}".format(the_id)):
        for nextrow in cursor.fetchall():
            retval = {'id': nextrow[0], 'lightcode': nextrow[1], 'monthmatch': nextrow[2], 'daymatch': nextrow[3], 'turnon': nextrow[4], 'turnoff': nextrow[5], 'hhcode': nextrow[6]}
    cursor.close()
    connection.close()
    #logit("get_light_schedule_detail {}: {}".format(the_id, retval))
    return retval

def set_light_schedule_detail(the_id, the_hhcode, the_lightcode, the_month, the_day, the_on_time, the_off_time, is_new):
    #logit('set_light_schedule_detail({}, {}, {}, {}, {}, {}, {}, {})'
          #.format(the_id, the_hhcode, the_lightcode, the_month,
                  #the_day, the_on_time, the_off_time, is_new))
    connection = db.open_sql_connection()
    the_cursor = connection.cursor()
    if is_new == 'true':
        the_sql = """INSERT INTO lightschedule (hhcode, lightcode, monthmatch, daymatch, turnon, turnoff)
                     VALUES ('{}', '{}', '{}', '{}', '{}', '{}')
                  """.format(the_hhcode, the_lightcode, the_month, the_day, the_on_time, the_off_time)
    else:
        the_sql = """UPDATE lightschedule SET hhcode='{}', lightcode='{}', monthmatch='{}', daymatch='{}', turnon='{}', turnoff='{}'
                     WHERE id={}
                  """.format(the_hhcode, the_lightcode, the_month, the_day, the_on_time, the_off_time, the_id)
    #logit("sql: " + the_sql)
    the_response = "no error"
    try:
        the_cursor.execute(the_sql)
        the_response = the_sql
    except Exception as ex:
        logit("failed to execute {} because {}".format(the_sql, ex))
        the_response = "{}".format(ex)
    the_cursor.close()
    connection.close()
    return the_response

def delete_light_schedule_detail(the_id):
    #logit('delete_light_schedule_detail({})'.format(the_id))
    the_response = "no error"
    connection = db.open_sql_connection()
    the_cursor = connection.cursor()
    the_sql = "DELETE FROM lightschedule WHERE id = {}".format(the_id)
    try:
        the_cursor.execute(the_sql)
        the_response = the_sql
    except Exception as ex:
        logit("failed to execute {} because {}".format(the_sql, ex))
        the_response = "{}".format(ex)
    the_cursor.close()
    connection.close()
    return the_response

def date_match(light_schedule):
    month = False
    day = False
    hour = False
    #logit("date_match {}".format(light_schedule))
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
    override = get_light_state(the_light) 
    if re.match('Auto',override):
        #if(month and day and hour):
            #logit("date_match {}".format(light_schedule))
        return month and day and hour
    else:
        #logit("Override: {} {}".format(light_schedule['lightcode'],override))
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
                sql = ("INSERT INTO lightschedule (hhcode, lightcode, monthmatch, daymatch, turnon, turnoff) "
                       "VALUES ('I', {}, '{}', '{}', '{}', '{}')"
                       "".format(nextlight, monthmatch, daymatch, turnon, turnoff))
                db.update_sql(sql)
                retval.append("Added new item to schedule<BR>")
    retval.append("<HR/><FORM METHOD=POST><SELECT NAME='PICKALIGHT' ID='PICKALIGHT' onChange='showOneLightSchedule();'>")
    retval.append("<OPTION VALUE='-1'>Choose a light</OPTION>")
    the_lights = get_light_list()
    for nextlight in the_lights:
        selected = ''
        if nextlight == pickalight:
            selected = ' SELECTED'
        retval.append("<OPTION VALUE='{}'{}>{}</OPTION>".format(nextlight, selected,  the_lights[nextlight]))
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

def process_light_schedule(the_light):
    current_state = get_light_state(the_light)
    new_state = "Off"
    if re.match('Auto', current_state):
        for nextrow in get_light_state_ids(the_light):
            if date_match(get_light_schedule_detail(nextrow)):
                new_state = "On"
        #logit("Light {} update state {}".format(light_list[the_light], new_state))
        apply_light_state(the_light, new_state)
    else:
        #logit("Light {} override {}".format(light_list[the_light], current_state))
        apply_light_state(the_light, current_state)

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
    for the_light in light_list:
        process_light_schedule(the_light)
        time.sleep(5)
    check_router()
    #pool = Pool()
    #pool.map(process_light_schedule, light_list)
    #pool.close()
