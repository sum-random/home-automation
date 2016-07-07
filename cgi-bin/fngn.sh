#!/usr/local/bin/bash

exec 2>&1

echo "Content-type: text/html; charset=iso-8859-1"
echo
echo "<HTML><HEAD><TITLE>$TITLE</TITLE>"
echo "</HEAD>"
echo "<BODY>"
echo "<TABLE><TR><TH>FNGN quote</TH></TR>"
/usr/local/bin/wget -O - -o /dev/null "http://investing.money.msn.com/investments/stock-price/?symbol=FNGN" | grep LastPrice | tr "<>" "\n" | grep [0-9] | while read FNGN; do
  echo "<TR><TD>$FNGN</TD></TR>";
done
echo "</TABLE>"
echo "</BODY></HTML>"

