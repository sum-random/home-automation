#!/usr/bin/env python3
"""scan devices for uptime, temperature, etc"""

import re
from subprocess import Popen, PIPE
from multiprocessing import Pool
import socket
import json
from datetime import datetime

import db
from config import config
CONFIG=config()

# Define some consts
APACHE=CONFIG['path']['www']
CGIDATA=CONFIG['path']['config']
USERSSH=CONFIG['path']['ssh']
SSHUSER=CONFIG['ssh']['user']
CMDS = { 2222: {'load': 'cat /proc/loadavg',
                'cpuinfo': 'which -s lscpu && lscpu | grep Model\ name || [ -f /proc/cpuinfo ] && cat /proc/cpuinfo | sed "s/\t*:/:/"',
                'batstat': 'cat /sys/class/power_supply/battery/uevent | grep STATUS | cut -d = -f 2',
                'batcap': 'cat /sys/class/power_supply/battery/uevent | grep CAPACITY | cut -d = -f 2'},
         22:   {'load': '[ -f /proc/loadavg ] && cat /proc/loadavg || sysctl vm.loadavg',
                'cpuinfo': 'which -s lscpu && lscpu | grep Model\ name || [ -f /proc/cpuinfo ] && cat /proc/cpuinfo | sed "s/\s*:/:/" || (sysctl -a  | grep -E "^hw.model|^hw.ncpu|^hw.physmem|^kern.version"; sysctl -a  | grep temperature | sed s/dev.cpu.[0-9]*/cpu/ | sort | uniq -c | tr -d : | awk \'{print $2" "$3": "$1}\')',
                'batstat': '[ -d  /sys/class/power_supply ] && cat /sys/class/power_supply/BAT0/uevent  | grep POWER_SUPPLY_STATUS | cut -d = -f 2',
                'batcap': '[ -d  /sys/class/power_supply ]  && cat /sys/class/power_supply/BAT0/capacity' } }
LOCKFILE = CONFIG['path']['lockfile']
CURTIME = int(datetime.timestamp(datetime.now()))


def _shortname(longname):
    """ return short form of hostname and parse out host info from dhcpd.conf """
    return longname.split('.')[0]

def readdevice(ipaddr):
    """get hostname, SSH port and device type"""
    fields = ['type', 'maker', 'model', 'version', 'misc1' , 'misc2']
    srv_type = {}
    try:
        host = socket.gethostbyaddr(ipaddr)
    except:
        host = [ipaddr]
    long = host[0]
    short = _shortname(long)
    spat = re.compile(short)
    mtype = re.compile(' *# type ')
    with open(CONFIG['path']['dhcpd_config'],encoding='utf-8') as f:
        while True:
            line = f.readline()
            if not line:
                break
            if spat.search(line):
                typeraw = f.readline()
                typeline = mtype.sub('', typeraw)[:-1]
                typeinfo = typeline.split(' ')
                for x in range(len(typeinfo)):
                    srv_type[fields[x]] = typeinfo[x]
                break
    srv_type['hostname'] = short
    if 'type' not in srv_type:
        srv_type['type'] = 'server'

    # merge previously saved info about this host
    update = db.get_device_info(srv_type['hostname'])
    if update:
        srv_type.update(update)

    return srv_type


def _device_ip_list():
    hosts = []
    with open(CONFIG['path']['named_config'], 'r', encoding='utf-8') as f:
        pat1 = re.compile('^[A-Za-z]')
        pat2 = re.compile('10.[45].[67][09].[0-9]*')
        pat3 = re.compile('10.10.10.[0-9]*')
        while True:
            line = f.readline()
            if not line:
                break
            if(pat1.search(line) and pat2.search(line)):
                match = pat2.search(line)
                hosts.append(readdevice(match.group()))
            if(pat1.search(line) and pat3.search(line)):
                match = pat3.search(line)
                hosts.append(readdevice(match.group()))
    return hosts


def check_ping(device):
    """ ping device and check for open SSH port"""
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
            except OSError:
                pass
            else:
                s.close()
                device['sshport'] = port
    return device


def check_ssh(device):
    """ Look for open SSH port, if found, log in and gather hardware info """
    if 'recd_pkts' in device and device['recd_pkts'] != '0' and 'sshport' in device:
        for key in CMDS[device['sshport']]:
            cmd=CMDS[device['sshport']][key]
            host=device['hostname']
            output = Popen([CONFIG['path']['ssh_cmd'],
                            "-f",
                            "-o", "StrictHostKeyChecking=no",
                            "-o", "HostkeyAlgorithms=+ssh-rsa",
                            "-o", "BatchMode=yes",
                            "-i", CONFIG['path']['ssh_key'],
                            "-p", f"{device['sshport']}",
                            f"{SSHUSER}@{host}",
                            f'{cmd}'], stdout=PIPE, stderr=PIPE)
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
                                device[key][keyval[0].strip().replace('.','_')] = keyval[1].strip()
                else:
                    device[key] = outtxt[:-1]
    return device


def scandevices():
    """ Scan devices in parallel
    Call _device_ip_list to get all devices, then
    check_ssh to scan each one and
    gather info if it has sshd daemon running
    """
    with Pool(16) as p:
        retval = p.map(check_ssh, p.map(check_ping, _device_ip_list()))
    return retval


def renderdevices():
    """ Attempt to read device into from the database
    Returns devices which responsed to ping during 
    most recent poll
    """
    retval = []
    connection = db.open_sql_connection()
    tablecursor = connection.cursor()
    query_string = "SELECT devjson FROM devices where json_value(devjson,'$.type') is not null;"
    if tablecursor.execute(query_string) > 0:
        for nexttable in tablecursor.fetchall():
            host_json = json.loads(nexttable[0])
            if 'recd_pkts' in host_json and host_json['recd_pkts'] != '0':
                if 'last_checked' in host_json and int(host_json['last_checked']) >= CURTIME-900:
                    retval.append(host_json)
    tablecursor.close()
    connection.close()
    return retval


def get_device_html():
    """ Render devices in a table for browser """
    # CPU type indexes
    lnx = 'model name'
    mip = 'cpu model'
    bsd = 'hw_model'
    arm = 'Processor'
    rpi = 'Model'
    armalt = 'CPU architecture'
    cpus = [lnx, mip, bsd, arm, rpi]

    try:
    # get the JSON data for rendering
        retval = ["<table><tr><th>Host</th><th>Type</th><th>Status</th><th>CPU</th><th>Charge</th></tr>"]
        for thehost in sorted(renderdevices(), key=lambda device: (device['type'], device['hostname'])):
            if 'batstat' in thehost or 'load' in thehost:
                batstat = thehost['batstat'] if 'batstat' in thehost else ''
                load = thehost['load'] if 'load' in thehost else ''
                hoststat = f"{batstat} {load}"
            else:
                hoststat = "Up"
            if 'batcap' in thehost and not isinstance(thehost['batcap'], dict):
                batcap = int(thehost['batcap'])
                batred = 255 if batcap < 50 else (100 - batcap) * 5
                batgrn = 255 if batcap > 50 else batcap * 5
                batcolor = f"rgb({batred},{batgrn},0)"
                batstat = f"<td style='background-color: {batcolor};'>{batcap}</td>"
            else:
                batstat = ''
            alttext = ''
            if 'cpuinfo' in thehost:
                cpuinfo = thehost['cpuinfo']
                new_cpuinfo = False
                if armalt in cpuinfo:
                    new_cpuinfo = f'{armalt}: ARM v{cpuinfo[armalt]}'
                for next_cpu  in cpus:
                    if next_cpu in cpuinfo:
                        new_cpuinfo = cpuinfo[next_cpu]
                if new_cpuinfo:
                    alttext = f'<td>{new_cpuinfo}</td>'
            retval.append(f"<tr><td>{thehost['hostname']}</td><td>{thehost['type']}</td><td>{hoststat}</td>{alttext}{batstat}</tr>")
        retval.append("</table><div name='cpuinfo'></div>")
        return '\n'.join(retval)
    except Exception as e:
        return f"{e}"


def get_device_info(host):
    """ Retrieve device info from db"""
    return db.get_device_info(host)

if __name__ == '__main__':
    for nextdev in scandevices():
        db.update_device_info(nextdev['hostname'],json.dumps(nextdev))
