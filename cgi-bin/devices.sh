#!/usr/local/bin/bash

APACHE="/usr/local/www/apache24"
CGIDATA="$APACHE/cgi-data"

USERSSH="$CGIDATA/.ssh"
SSHAUTH="-i $USERSSH/id_rsa"
SSHOPTIONS="$SSHAUTH -o StrictHostKeyChecking=no -o PasswordAuthentication=no"
lname[50]="ctucker"
lname[51]="ctucker"
lname[64]="ctucker"
lname[66]="ctucker"
lname[102]="ctucker"
lname[106]="ctucker"
lname[107]="ctucker"
lname[113]="ctucker"

getRGB() {
	NM=$1
        [ -z "$1" ] && NM=0
	[ "$1" -gt 100 ] && NM=100
	RC=$(if [ "$NM" -lt 50 ] ; then echo FF ; else printf "%02X" "$((255 - 255 * ($NM-50) / 50))" ; fi )
	GC=$(if [ "$NM" -ge 50 ] ; then echo FF ; else printf "%02X" "$((255 * $NM / 50))" ; fi )
	printf "${RC}${GC}00"
}

readdevice() {
	HN=$( nslookup $1 | grep name | sed -e 's/.*= //' -e 's/.claytontucker.*//' | tail -1)
        TYPE=$(grep -iA 4 \ $HN\  /usr/local/etc/dhcpd.conf | grep type  | awk '{print $3}')
        EXACT=$(grep -iA 4 \ $HN\  /usr/local/etc/dhcpd.conf | grep type  | awk '{print $4" "$5" "$6}')
	STATS=$(if nc -zw 1 $1 2222 2>&1 | grep -qi succeeded ; then 
		ST=$(ssh -q -l root $SSHOPTIONS -p 2222 $1 'cat /sys/class/power_supply/battery/uevent' | grep 'STATUS' | cut -d = -f 2)
		LD=$(ssh -q -l root $SSHOPTIONS -p 2222 $1 'cat /proc/loadavg')
		PCT=$(ssh -q -l root $SSHOPTIONS -p 2222 $1 'cat /sys/class/power_supply/battery/uevent' | grep 'CAPACITY' | cut -d = -f 2)
		RGB=$(getRGB $PCT)
		printf "<TD>$ST $LD</TD><TD STYLE='background-color:#${RGB};'>$PCT</TD>"  
	elif nc -zw 1 $1 22 2>&1 | grep -qi succeeded ; then
		BATCAP=""
		PWRSTAT=""
		RGB=""
	        IDX=$(echo $1 | sed -e 's/[0-9]*\.[0-9]*\.[0-9]*\.\([0-9]*\)/\1/')
		printf "<TD>"
		if [ -n "$IDX" ] && [ -n "${lname[$IDX]}" ] ; then
                        THELOGIN=${lname[$IDX]}
			PWRSTAT=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts $SSHOPTIONS -n ${THELOGIN}@$IP "cat /sys/class/power_supply/BAT0/uevent | grep POWER_SUPPLY_STATUS | cut -d = -f 2" 2>/dev/null)
			BATCAP=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts $SSHOPTIONS -n ${THELOGIN}@$IP "cat /sys/class/power_supply/BAT0/capacity" 2>/dev/null)
			[ -n "$BATCAP" ] && RGB=$(getRGB $BATCAP)
			LOADAVG=""
			LOADAVG=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts $SSHOPTIONS -n ${THELOGIN}@$IP "cat /proc/loadavg" 2>/dev/null)
			[ -z "$LOADAVG" ] && LOADAVG=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts $SSHOPTIONS -n ${THELOGIN}@$IP "sysctl vm.loadavg" 2>/dev/null)
		fi
		[ -n "$PWRSTAT" ] && printf "$PWRSTAT "
		[ -n "$LOADAVG" ] && printf "$LOADAVG"
		printf "</TD>"
		[ -n "$RGB" ] && printf "<TD STYLE='background-color:#${RGB};'>$BATCAP</TD>"
	elif ping -c 2 $1 >/dev/null 2>&1; then
		printf "<TD>Up</TD>"
	else
		printf "<TD>Down</TD>"
	fi)
	printf "<TR><TD>$HN</TD><TD>$TYPE</TD>$STATS</TR>\n";
}

for IP in $( cat /usr/local/etc/namedb/master/claytontucker.org | grep ^[A-Za-z] | grep 10.4.69 | awk '{print $4}' | sort | uniq); do
	readdevice $IP >>$CGIDATA/devices.new.txt 2>&1  &
done 
wait
mv -f $CGIDATA/devices.new.txt $CGIDATA/devices.txt
