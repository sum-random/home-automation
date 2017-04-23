#!/usr/local/bin/bash
echo "Content-type: text/plain; charset=iso-8859-1"
echo

/usr/local/bin/wget -qO - http://gimp-print.sourceforge.net/p_Supported_Printers.php | grep '<tr><td>' | sed -e 's/<tr><td>//' -e 's/<\/td><td>.*//' | sort | grep -v Welcome
