#!/usr/local/bin/bash

exec 2>&1

echo "Content-type: text/html; charset=iso-8859-1"
echo
echo "<HTML><HEAD><TITLE>$TITLE</TITLE>"
echo "</HEAD>"
echo "<BODY>"
echo "<TABLE><TR><TH>Filesystem</TH><TH>1M-blocks</TH><TH>Used</TH><TH>Avail</TH><TH>Capacity</TH><TH>Mounted on</TH></TR>"
df -m | grep local/media | while read FS BC US AV CP MP; do
  echo "<TR><TD>$FS</TD><TD>$BC</TD><TD>$US</TD><TD>$AV</TD><TD>$CP</TD><TD>$MP</TD></TR>";
done
echo "</TABLE>"
echo "</BODY></HTML>"

