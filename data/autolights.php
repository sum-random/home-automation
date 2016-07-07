#!/usr/local/bin/bash

exec 2>&1
LOGFILE=/tmp/lights.log

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
 sleep 5
 rm -f $LOCKFILE
}


#contants
LOGFILE=/tmp/lights.log
BASE=/usr/local/www/apache24/cgi-data
OFFSET=3
HOUSECODE=i
RPT="-r 5"
BR="/usr/local/bin/br -x /dev/cuau0 -c $HOUSECODE"
BR="/usr/local/bin/br -x /dev/cuau0 -c $HOUSECODE $RPT"
SEP=","

#presets
DEVFILE="$BASE/lights.dat"
[ -f "$DEVFILE" ] || exit 1
DEVCNT=`cat $DEVFILE | wc -l`
HR=`date '+%H'`
HR=`expr $HR + $OFFSET`

br_cmd_off() {
      DEV=$1
      getlock
      $BR -f $DEV
      droplock
      echo "`date '+%H%M%S'` $HR OFF:$DEV" >>$LOGFILE
}
br_cmd_on() {
      DEV=$1
      getlock
      $BR -n $DEV
      droplock
      echo "`date '+%H%M%S'` $HR ON: $DEV" >>$LOGFILE
}
br_cmd_dim() {
      DEV=$1
      LEV=$2
      getlock
      $BR -d $LEV,$DEV
      droplock
      echo "`date '+%H%M%S'` $HR DIM:$DEV" >>$LOGFILE
}

cat $DEVFILE | while read THISLN ; do
  THISDEVID=`echo $THISLN | cut -f 1 -d $SEP`
  THISDEVSET=`echo $THISLN | cut -f $HR -d $SEP`
  [ -f "$BASE/DEV${THISDEVID}" ] && THISDEVSET=`cat $BASE/DEV${THISDEVID}`
  if [ "$THISDEVSET" = "On" ] ; then
    br_cmd_on $THISDEVID
  else
    br_cmd_off $THISDEVID
  fi
done


