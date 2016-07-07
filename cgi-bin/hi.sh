#!/usr/local/bin/bash

exec 2>&1

echo "Content-type: text/html; charset=iso-8859-1"
echo
echo "<HTML><HEAD><TITLE>$TITLE</TITLE>"
echo "</HEAD>"
echo "<BODY>"
printf '<H1>Hello, World!</H1>\n'
echo "</BODY></HTML>"

