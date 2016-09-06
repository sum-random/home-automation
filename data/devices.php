<TABLE><TR><TH>Host</TH><TH>Status</TH><TH>Charge</TH></TR>
<?php

	system("cat ../cgi-data/devices.txt | sort -f | grep -av Down");
?>
</TABLE>
