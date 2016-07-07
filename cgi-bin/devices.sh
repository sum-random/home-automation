#!/usr/local/bin/bash

USERSSH="/usr/local/www/apache24/cgi-data/.ssh"
lname[1]="ctucker"
lname[50]="ctucker"
lname[64]="ctucker"
lname[66]="ctucker"
lname[96]="ctucker"
lname[99]="thanvalai"
lname[102]="nathan"
lname[103]="thanvalai"
lname[141]="ctucker"

getRGB() {
	NM=$1
	[ "$1" -gt 100 ] && NM=100
	RC=$(if [ "$NM" -lt 50 ] ; then echo FF ; else printf "%02X" "$((255 - 255 * ($NM-50) / 50))" ; fi )
	GC=$(if [ "$NM" -ge 50 ] ; then echo FF ; else printf "%02X" "$((255 * $NM / 50))" ; fi )
	printf "${RC}${GC}00"
}

readdevice() {
	HN=$(grep "^$1\W" /etc/hosts | awk '{print $2}') 
	CL=$(grep "^$1\W" /etc/hosts | awk '{print $3}') 
	STATS=$(if nc -zw 1 $1 2222 2>&1 | grep -qi succeeded ; then 
		ST=$(ssh -q -l root -i /usr/local/www/apache24/cgi-data/.ssh/id_dsa -o StrictHostKeyChecking=no -p 2222 $1 'cat /sys/class/power_supply/battery/uevent' | grep 'STATUS' | cut -d = -f 2)
		LD=$(ssh -q -l root -i /usr/local/www/apache24/cgi-data/.ssh/id_dsa -o StrictHostKeyChecking=no -p 2222 $1 'cat /proc/loadavg')
		PCT=$(ssh -q -l root -i /usr/local/www/apache24/cgi-data/.ssh/id_dsa -o StrictHostKeyChecking=no -p 2222 $1 'cat /sys/class/power_supply/battery/uevent' | grep 'CAPACITY' | cut -d = -f 2)
		RGB=$(getRGB $PCT)
		printf "<TD>$ST $LD</TD><TD STYLE='background-color:#${RGB};'>$PCT</TD>"  
	elif nc -zw 1 $1 22 2>&1 | grep -qi succeeded ; then
		BATCAP=""
		PWRSTAT=""
		RGB=""
	        IDX=$(echo $1 | sed -e 's/[0-9]*\.[0-9]*\.[0-9]*\.\([0-9]*\)/\1/')
		printf "<TD>"
		if [ -n "$IDX" ] && [ -n "${lname[$IDX]}" ] ; then
			PWRSTAT=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts -o StrictHostKeyChecking=no -o PasswordAuthentication=no -i $USERSSH/id_dsa -n ${lname[$IDX]}@$IP "cat /sys/class/power_supply/BAT0/uevent | grep POWER_SUPPLY_STATUS | cut -d = -f 2" 2>/dev/null)
			BATCAP=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts -o StrictHostKeyChecking=no -o PasswordAuthentication=no -i $USERSSH/id_dsa -n ${lname[$IDX]}@$IP "cat /sys/class/power_supply/BAT0/capacity" 2>/dev/null)
			[ -n "$BATCAP" ] && RGB=$(getRGB $BATCAP)
			LOADAVG=""
			LOADAVG=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts -o StrictHostKeyChecking=no -o PasswordAuthentication=no -i $USERSSH/id_dsa -n ${lname[$IDX]}@$IP "cat /proc/loadavg" 2>/dev/null)
			[ -z "$LOADAVG" ] && LOADAVG=$(ssh -o UserKnownHostsFile=$USERSSH/known_hosts -o StrictHostKeyChecking=no -o PasswordAuthentication=no -i $USERSSH/id_dsa -n ${lname[$IDX]}@$IP "sysctl vm.loadavg" 2>/dev/null)
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
	printf "<TR><TD>$CL</TD><TD>$HN</TD>$STATS</TR>\n";
}

for IP in $(cat /etc/hosts | grep -vE '::1|127.0.0.1|10.4.69.[0-9]\W|^#' | awk '{print $1}'); do
	readdevice $IP >>/usr/local/www/apache24/cgi-data/devices.new.txt 2>&1  &
done 
wait
mv -f /usr/local/www/apache24/cgi-data/devices.new.txt /usr/local/www/apache24/cgi-data/devices.txt
