#!/bin/sh
HOME=/usr/local/www/apache24/cgi-data

# disable filename globbing
set -f

#10.4.69.64 Io
#10.4.69.102 Amalthea-wired
#10.4.69.98 Metis

netCheck() {
for LOGIN in ctucker@io visitor@metis nathan@amalthea kaimook@adrastea; do
  HIP=`echo $LOGIN | cut -d @ -f 2`
  if ping -qc 2 $HIP 2>/dev/null 1>/dev/null ; then
    HN=`cat /etc/hosts | grep $HIP\  | awk '{print $2}' | tail -1`
    echo "<H1>Host $HIP is up</H1>"
    ssh -o StrictHostKeyChecking=no -n $LOGIN "ps -ef;lsof | grep /home/ | sed -e 's/.*\(\/home\/.*\)/\1/' | sort | uniq" 2>&1
  fi
done

}
echo "Content-type: text/html; charset=iso-8859-1"
echo

echo "<HTML><HEAD><TITLE>Local systems check</TITLE></HEAD><BODY>"

netCheck | while read NXTLINE ; do
  printf "%s<BR>\n" "$NXTLINE"
done

echo "</BODY>"

