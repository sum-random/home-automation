#!/usr/bin/env python3

import re
import os
import subprocess
from subprocess import Popen, PIPE
from multiprocessing import Pool
import socket
import json
import syslog
import time
from datetime import datetime

import db
from logit import logit
from config import config
CONFIG=config()

# Define some consts
APACHE=CONFIG['path']['www']
CGIDATA=CONFIG['path']['config']
USERSSH=CONFIG['path']['ssh']
SSHUSER=CONFIG['ssh']['user']
CMDS = { 2222: {'load': 'cat /proc/loadavg',
                'cpuinfo': '[ -f /proc/cpuinfo ] && cat /proc/cpuinfo | sed "s/\t*:/:/"',
                'batstat': 'cat /sys/class/power_supply/battery/uevent | grep STATUS | cut -d = -f 2',
                'batcap': 'cat /sys/class/power_supply/battery/uevent | grep CAPACITY | cut -d = -f 2'},
         22:   {'load': '[ -f /proc/loadavg ] && cat /proc/loadavg || sysctl vm.loadavg',
                'cpuinfo': '[ -f /proc/cpuinfo ] && cat /proc/cpuinfo | sed "s/\s*:/:/" || (sysctl -a  | grep -E "^hw.model|^hw.ncpu|^hw.physmem|^kern.version"; sysctl -a  | grep temperature | sed s/dev.cpu.[0-9]*/cpu/ | sort | uniq -c | tr -d : | awk \'{print $2" "$3": "$1}\')',
                'batstat': '[ -d  /sys/class/power_supply ] && cat /sys/class/power_supply/BAT0/uevent  | grep POWER_SUPPLY_STATUS | cut -d = -f 2',
                'batcap': '[ -d  /sys/class/power_supply ]  && cat /sys/class/power_supply/BAT0/capacity' } }
LOCKFILE = CONFIG['path']['lockfile']
CURTIME = '{}'.format(int(datetime.timestamp(datetime.now())))


def _shortname(longname):
    """ return short form of hostname and parse out host info from dhcpd.conf """
    return longname.split('.')[0]

def readdevice(ipaddr):
    the_srv_type = {}
    try:
    	hostname = socket.gethostbyaddr(ipaddr)
    except:
        hostname = [ipaddr]
    dom = re.compile('.claytontucker.org')
    long = hostname[0]
    short = _shortname(long)
    spat = re.compile(short)
    type = re.compile(' *# type ')
    f = open(CONFIG['path']['dhcpd_config'])
    while True:
        line = f.readline()
        if not line: break
        if spat.search(line):
            typeraw = f.readline()
            typeline = type.sub('', typeraw)[:-1]
            typeinfo = typeline.split(' ')
            fields = ['type', 'maker', 'model', 'version', 'misc1' , 'misc2']
            for x in range(len(typeinfo)):
              the_srv_type[fields[x]] = typeinfo[x]
            break
    f.close()
    the_srv_type['hostname'] = short
    if not 'type' in the_srv_type:
        the_srv_type['type'] = 'server'

    # get SSH port number, if previously saved
    connection = db.open_sql_connection()
    cursor = connection.cursor()
    the_sql = "SELECT JSON_EXTRACT(devjson,'$.sshport') FROM devices where hostname='{}';".format(short)
    if cursor.execute(the_sql) > 0:
        for nextrow in cursor.fetchall():
            if nextrow[0] is not None:
                the_srv_type['sshport'] = int(nextrow[0])
    cursor.close()
    connection.close()

    return(the_srv_type)


def _device_ip_list():
    hosts = []
    f = open(CONFIG['path']['named_config'], 'r')
    pat1 = re.compile('^[A-Za-z]')
    pat2 = re.compile('10.4.[67][09].[0-9]*')
    pat3 = re.compile('10.10.10.[0-9]*')
    while True:
        line = f.readline()
        if not line: break
        if(pat1.search(line) and pat2.search(line)):
            match = pat2.search(line)
            hosts.append(readdevice(match.group()))
        if(pat1.search(line) and pat3.search(line)):
            match = pat3.search(line)
            hosts.append(readdevice(match.group()))
    f.close()
    return hosts


def check_ping(device):
    dev_name = device['hostname']
    ping_pat = re.compile('.*(\d) packets received.*')
    output = ','.join(Popen(["/sbin/ping",
                             "-c", "5",
                             "-t", "1",
                             dev_name], stdout=PIPE,stderr=PIPE)
                          .communicate()[0].decode('utf-8').split('\n'))
    recd_pkts = ping_pat.match(output)
    if recd_pkts:
        device['recd_pkts'] = recd_pkts.groups(0)[0]
    else:
        device['recd_pkts'] = '0'
    device['last_checked'] = CURTIME
    if device['recd_pkts'] != '0' and 'sshport' not in device:
        for port in [22,2222]:
            try:
                socket.setdefaulttimeout(3)
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((dev_name, port))
            except OSError as error:
                pass
            else:
                s.close()
                device['sshport'] = port
    return device


def check_ssh(device):
    """ Look for open SSH port, if found, log in and gather hardware info """
    dev_name = device['hostname']
    if 'recd_pkts' in device and device['recd_pkts'] != '0' and 'sshport' in device:
        for key in CMDS[device['sshport']]:
            output = Popen([CONFIG['path']['ssh_cmd'],
                            "-f",
                            "-o", "StrictHostKeyChecking=no",
                            "-o", "BatchMode=yes",
                            "-i", CONFIG['path']['ssh_key'],
                            "-p", "{}".format(device['sshport']),
                            "{}@{}".format(SSHUSER, device['hostname']),
                            '{}'.format(CMDS[device['sshport']][key])], stdout=PIPE, stderr=PIPE)
            output.wait()
            outtxt = output.communicate()[0].decode('utf-8')
            if outtxt:
                if re.search('COMMAND SYNTAX ERROR', outtxt):
                    pass
                elif '\n' in outtxt[:-1]:
                    device[key] = {}
                    for devitem in outtxt.split('\n'):
                        if ':' in devitem:
                            keyval = devitem.split(':')
                            if len(keyval) >= 2:
                                jskeys = keyval[0].split('.')
                                device[key][keyval[0].strip()] = keyval[1].strip()
                else:
                    device[key] = outtxt[:-1]
    return device


def scandevices():
    """ Scan devices in parallel
    Call _device_ip_list to get all devices, then
    check_ssh to scan each one and
    gather info if it has sshd daemon running
    """
    p = Pool(16)
    retval = p.map(check_ssh, p.map(check_ping, _device_ip_list()))
    p.close()
    p.join()
    return retval


def renderdevices():
    """ Attempt to read device into from the database
    Returns devices which responsed to ping during 
    most recent poll
    """
    retval = []
    connection = db.open_sql_connection()
    tablecursor = connection.cursor()
    the_sql = "SELECT devjson FROM devices where json_value(devjson,'$.type') is not null;"
    if tablecursor.execute(the_sql) > 0:
        for nexttable in tablecursor.fetchall():
            the_host_json = json.loads(nexttable[0])
            if 'recd_pkts' in the_host_json and the_host_json['recd_pkts'] != '0':
                retval.append(the_host_json)
    tablecursor.close()
    connection.close()
    return retval


def get_device_html():
  # CPU type indexes
  lnx = 'model name'
  bsd = 'hw.model'
  arm = 'Processor'
  armalt = 'CPU architecture'
  try:
    """ Render devices in a table for browser """
    # get the JSON data for rendering
    retval = ["<table><tr><th>Host</th><th>Type</th><th>Status</th><th>CPU</th><th>Charge</th></tr>"]
    for thehost in sorted(renderdevices(), key=lambda device: (device['type'], device['hostname'])):
        shorthost = _shortname(thehost['hostname'])
        if 'batstat' in thehost or 'load' in thehost:
            hoststat = "{} {}".format(thehost['batstat'] if 'batstat' in thehost else '',
                                      thehost['load'] if 'load' in thehost else '')
        else:
            hoststat = "Up"
        if 'batcap' in thehost and not isinstance(thehost['batcap'], dict):
            batcap = int(thehost['batcap'])
            batred = 255 if batcap < 50 else (100 - batcap) * 5
            batgrn = 255 if batcap > 50 else batcap * 5
            batcolor = "rgb({},{},0)".format(batred, batgrn)
            batstat = "<td style='background-color: {};'>{}</td>".format(batcolor, batcap)
        else:
            batstat = ''
        alttext = ''
        if 'cpuinfo' in thehost:
            cpuinfo = thehost['cpuinfo']
            the_cpu = False
            if lnx in cpuinfo:
                the_cpu = cpuinfo[lnx]
            if bsd in cpuinfo:
                the_cpu = cpuinfo[bsd]
            if armalt in cpuinfo:
                the_cpu = '{}: ARM v{}'.format(armalt, cpuinfo[armalt])
            if arm in cpuinfo:
                the_cpu = cpuinfo[arm]
            if the_cpu:
                alttext = '<td>{}</td>'.format(the_cpu)
        retval.append("<tr><td>{}</td><td>{}</td><td>{}</td>{}{}</tr>".format(thehost['hostname'],
                                                                                thehost['type'],
                                                                                hoststat,
                                                                                alttext,
                                                                                batstat))
    retval.append("</table><div name='cpuinfo'></div>")
    return '\n'.join(retval)
  except Exception as e:
    return "{}".format(e)
    

def get_device_info(the_host):
    """ Return device info """
    retval = False
    connection = db.open_sql_connection()
    tablecursor = connection.cursor()
    the_sql = "SELECT devjson FROM devices WHERE hostname='{}'".format(the_host)
    if tablecursor.execute(the_sql) > 0:
        for nexttable in tablecursor.fetchall():
            the_host_json = json.loads(nexttable[0])
            if the_host_json['recd_pkts'] != '0' and 'cpuinfo' in the_host_json:
                retval = the_host_json['cpuinfo']
    tablecursor.close()
    connection.close()
    return retval
    
if __name__ == '__main__':
    connection = db.open_sql_connection()

    for nextdev in scandevices():
        tablecursor = connection.cursor()
        the_sql = "INSERT INTO devices(hostname, devjson) VALUES('{0}', '{1}') ON DUPLICATE KEY UPDATE devjson='{1}';".format(nextdev['hostname'], json.dumps(nextdev))
        tablecursor.execute(the_sql)
        connection.commit()
    connection.close()
