#!/usr/local/bin/bash

exec 2>&1

TMP=/tmp
WORK="$TMP/$$"
# Split the encoded data into name=value pairs
BASE=/usr/local/www/apache24/cgi-data
#OPTS=`cat - | sed 's/&/ /g'`
OPTS="`echo $QUERY_STRING | tr \& "\n" | grep =`"
DEVS="`mixer | grep -v source | cut -f 2 -d \ `"
HOUSECODE=i
RPT="-r 5"
BR="/usr/local/bin/br -x /dev/cuau0 -c $HOUSECODE $RPT"

mkdir -p $WORK

br_cmd_dim() {
      DEV=$1
      LEV=$2
      $BR -d $LEV,$DEV
      sleep 3
}

echo "Content-type: text/html; charset=iso-8859-1"
echo
# Decode the form data
for opt in $OPTS; do
   NAME=`echo $opt | sed 's/=/ /g' | awk '{print $1}'`
   VALUE="`echo $opt | sed 's/=/ /g' | awk '{print $2}' | \
          sed 's,%,\\\x,g' | \
          sed 's~\\\x2C~,~g' | \
          sed 's/+/ /g'`"
   if echo "$NAME" | grep -q ^DEV ; then
      FN=$BASE/DEV${VALUE}
      if [ -f $FN ] ; then
        RV=`cat $FN`
      else
        RV="AUTO"
      fi
      printf "${VALUE}:${RV}"
   fi
done
rm -r $WORK
