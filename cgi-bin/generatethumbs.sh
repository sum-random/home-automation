#!/usr/local/bin/bash

WORK="/usr/local/www/apache24/cgi-data"

rm -f $WORK/thumblist2.txt $WORK/thumblist3.txt

LNCNT=0

find /usr/local/media/Image -type f | grep -iE "jpg|gif|jpeg|png" | grep -i thumbsize | while read FN ; do
  SF="/img`echo "$FN" | cut -b 23-`" ; 
  IMGVAL=`identify -verbose "$FN" | grep mean | head -3 | tr \. \  | awk '{print $2}' | tr "\n" \ `; 
  echo $IMGVAL | grep -q \  || IMGVAL="$IMGVAL $IMGVAL $IMGVAL"
  MD5=`md5 "$FN" | cut -f 2 -d =`
  [ -z "$IMGVAL" ] || printf "%s:%02X%02X%02X:%s\n" $MD5 $IMGVAL "$SF"  
done | sort | while read EACH ; do 
  MD5=`echo $EACH | cut -f 1 -d :`
  CLR=`echo $EACH | cut -f 2 -d :`
  PTH=`echo $EACH | cut -f 3 -d :`
  TFN=`basename "$PTH"`
  [ "$MD5" = "$LMD5" ] || [ -z "$CLR" ] || [ -z "$PTH" ] || echo "$CLR $PTH";
  LMD5="$MD5"
done > $WORK/thumblist2.txt

mv $WORK/thumblist2.txt $WORK/thumblist.txt
