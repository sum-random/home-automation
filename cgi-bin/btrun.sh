#!/usr/local/bin/bash

cd /home/ctucker
LOG="/tmp/torrent.log"
touch $LOG
LOGSZ=`ls -l $LOG | awk '{print $5}'`
BTHOME="/home/ctucker/bt"
if [ "$LOGSZ" -gt 50000000 ] ; then
  pkill python
  mv $BTHOME/work/*torrent $BTHOME/
fi
DLRATE=`grep download\ rate: $LOG  | awk '{print $3}' | tr -d \. | tail -1`
DLCNT=`grep download\ rate: $LOG  | uniq -c | sed -e 's/\([0-9]*\) download rate:  \([0-9.]*\) KB\/s/\1 \2/' | tail -1 | awk '{print $1}'`
[ -z "$DLRATE" ] && DLRATE=0
[ "$DLRATE" = "---" ] && DLRATE=0
[ -z "$DLCNT" ] && DLCNT=0
PCTDONE=`grep percent\ done: $LOG | tail -2 | head -1 | tr -d "." | cut -d : -f 2`
DLSTATE=""
MAXWAIT=`expr 100 + $PCTDONE`
MAXWAIT=`expr $MAXWAIT / 2`

start_torrent() { 
  NXT=`ls $BTHOME/work/ | grep torrent | head -1`
  if [ -z "$NXT" ] ; then
    CNT=`ls $BTHOME/ | grep torrent | wc -l`
    [ "$CNT" -eq 0 ] && exit
    POS=$((RANDOM % CNT + 1))
    NXT=`ls $BTHOME/ | grep torrent | head -$POS | tail -1`
    mkdir -p $BTHOME/work
    sudo mv "$BTHOME/$NXT" "$BTHOME/work/"
  fi
  echo "Rotate log"
  [ -f $LOG ] && (mv $LOG $LOG.old ; cat $LOG.old | tail -1000 >$LOG ; rm -f $LOG.old;)
  echo "Starting $NXT"
  MAXUP=" --max_upload_rate 50000 "
  MAXIN=" --max_initiate 5 "
  MAXAL=" --max_allow_in 10 "
  SAVIN=" --save_in $BTHOME/downloads/ --save_incomplete_in $BTHOME/incomplete "
  VRBSE=" --spew "
  NEWCN=" --rerequest_interval 60 "
  DATDR=" --data_dir $BTHOME/console "

  [ -n "$BTHOME/$NXT" ] && nice sudo /usr/local/bin/bittorrent-console $MAXUP $MAXIN $MAXAL $SAVIN $VRBSE $NEWCN $DATDR "$BTHOME/work/$NXT" 2>&1 >>$LOG &
}

if [ -n "`pgrep python`" ] ; then
  STATE=`grep time\ left $LOG | tail -1 | cut -d : -f 2 | tr -d \ `
  PEERS=`grep peer\ status $LOG | tail -1 | cut -d : -f 2 | awk '{print $1}'`
  echo "DLRATE=$DLRATE DLCNT=$DLCNT" >>$LOG
  [ "$DLRATE" -lt 10 ] && [ "$DLCNT" -gt $MAXWAIT ] && DLSTATE="stopped"
  if [ "$STATE" = "seeding" ] ; then
    RATING=`tail -500 $LOG | grep share\ rating | awk '{print $3}' | tr -d '\.' | cut -b -2 | tail -1`
    [ "$RATING" = "oo" ] && RATING="15"
    #RATING="1"
    if [ "$RATING" -ge 12 ] || [ "0$PEERS" -eq 0 ] ; then
      pkill python
      NXT=`ls $BTHOME/work/ | grep torrent | head -1`
      mv "$BTHOME/work/$NXT" "$BTHOME/downloads/"
      start_torrent
    fi
  elif [ "$DLSTATE" = "stopped" ] ; then
    # return torrent to ready pool
    pkill python
    NXT=`ls $BTHOME/work/ | grep torrent | head -1`
    if [ "$PCTDONE" -eq 0 ] ; then
      mv "$BTHOME/work/$NXT" "$BTHOME/wait/"
    else
      mv "$BTHOME/work/$NXT" "$BTHOME/"
    fi
    sleep 10
    start_torrent
  elif [ "$STATE" = "stopped" ] ; then
    # restart stopped torrent
    pkill python
    sleep 10
    start_torrent
  fi
else
  start_torrent
fi
