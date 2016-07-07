#!/usr/local/bin/bash

exec 2>&1

TMP=/tmp
LOGFILE=/tmp/lights.log
WORK="$TMP/$$"
# Split the encoded data into name=value pairs
BASE=/usr/local/www/apache24/cgi-data
#OPTS=`cat - | sed 's/&/ /g'`
OPTS="`echo $QUERY_STRING | tr \& "\n" | grep =`"
HOUSECODE=i
RPT="-r 5"
BR="/usr/local/bin/br -x /dev/cuau0 -c $HOUSECODE $RPT"
BR="/usr/local/bin/br -x /dev/cuau0 -vvv -c $HOUSECODE "

mkdir -p $WORK

getlock() {
 LOCKFILE=/tmp/br.lock
 LOCKWAIT=20
 while [ -f $LOCKFILE ] ;  do
  sleep $LOCKWAIT
  LOCKWAIT=`expr $LOCKWAIT - 1`
  [ $LOCKWAIT -eq 0 ] && exit 0
 done
 touch $LOCKFILE
}

droplock() {
 LOCKFILE=/tmp/br.lock
 rm -f "$LOCKFILE"
}

br_cmd_off() {
      DEV=$1
      getlock
      $BR -f $DEV
      droplock
      sleep 1
      echo "OFF:$DEV" >>$LOGFILE
}

br_cmd_on() {
      DEV=$1
      getlock
      $BR -n $DEV
      droplock
      sleep 1
      echo "ON: $DEV" >>$LOGFILE
}

br_cmd_dim() {
      DEV=$1
      LEV=$2
      getlock
      $BR -d $LEV,$DEV
      droplock
      sleep 1
      echo "DIM:$DEV" >>$LOGFILE
}

echo "Content-type: text/html; charset=iso-8859-1"
echo
echo "<HTML><HEAD><TITLE>SetOneLight</TITLE>"
echo "</HEAD>"
echo "<BODY>"
# Decode the form data
echo "$OPTS"
for opt in $OPTS; do
   NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
   VALUE="`echo $opt | sed 's/=/ /g' | awk '{print $2}' | \
          sed 's,%,\\\x,g' | \
          sed 's~\\\x2C~,~g' | \
          sed 's/+/ /g'`"
#   printf "<LI><B>$NAME:</B>:$VALUE:"
   if echo "$NAME" | grep -q ^DEV ; then
      DV="`echo $NAME | cut -b 4-`"
#      echo "<BR>/usr/sbin/mixer $DV $VALUE:$VALUE <BR>" 
      FN=$BASE/DEV${DV}
      echo "$VALUE" > $FN
      if [ "$VALUE" = "AUTO" ] ; then
        echo "Release light $DV $FN<BR>"
        rm -f $FN
      elif [ "$VALUE" = "Off" ] ; then
        echo "Turn off light $DV $FN<BR>"
        br_cmd_off $DV
      else
        echo "Set light $DV to $VALUE<BR>"
        if [ "$VALUE" = "On" ] ; then
          br_cmd_on $DV
        else
          br_cmd_dim $DV $VALUE
        fi
      fi
   fi
done
#echo $OPTS
rm -r $WORK
echo "</BODY></HTML>"
