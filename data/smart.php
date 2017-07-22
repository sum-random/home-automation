<HTML>
<HEAD>
<TITLE>Home page</TITLE>
<STYLE>
p {font-family:monospace;}
</STYLE>
</HEAD>
<BODY>
  <FORM METHOD="POST">
    <SELECT NAME="theDisk" onChange='submit();'>
      <OPTION VALUE="">Choose the device to query</OPTION>
      <OPTION VALUE="ada0">RaidZ0</OPTION>
      <OPTION VALUE="ada1">RaidZ1</OPTION>
      <OPTION VALUE="ada2">RaidZ2</OPTION>
      <OPTION VALUE="ada3">boot</OPTION>
    </SELECT>
  </FORM>
  <P>
<?php 

  if(array_key_exists("theDisk",$_REQUEST)) {
    $cmd = "/usr/local/bin/sudo /usr/local/sbin/smartctl -a /dev/" . $_REQUEST['theDisk'] . " | sed 's/$/<BR>/'";
    echo "Device " . $_REQUEST['theDisk'] . ":<BR>";
    passthru($cmd);
  }
 ?>
  </P>
</BODY>
</HTML>

