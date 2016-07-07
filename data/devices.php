<TABLE><TR><TH>Class</TH><TH>Host</TH><TH>Status</TH><TH>Charge</TH></TR>
<?php

	system("cat ../cgi-data/devices.txt | sort | grep -av Down");
?>
</TABLE>
