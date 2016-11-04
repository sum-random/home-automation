<!DOCTYPE HTML>
<HTML><HEAD><TITLE>Play Music</TITLE>
<?php
include("inc/pdo.php");

global $mysql,$base;
$base="/usr/local/media/";



function stop_play() { 
  shell_exec("kill -9 $(ps wwaux | grep -v grep | grep mpg123 | awk '{print $2}') 2>/dev/null; rm -f /tmp/tracks*");
}

function get_devices() {
  $droids = Array();
  $droids['GalaxyS3'] = '10.4.69.130';
  $droids['GalaxyS4'] = '10.4.69.138';
  $droids['GalaxyS5'] = '10.4.69.140';
  $droids['GalaxyS6'] = '10.4.69.142';
  $droids['GalaxyTab'] = '10.4.69.144';
  $droids['GalaxyNote'] = '10.4.69.136';
  foreach($droids as $host => $ip) {
    $connection = @fsockopen($ip, 2222, $errno, $errstr, 1);
    if (is_resource($connection))
      fclose($connection);
    else
      unset($droids[$host]);
  }
  return $droids;
  //return preg_split('/[\n]/',shell_exec('grep Galaxy /etc/namedb/master/claytontucker.export | awk \'{print $4" "$1}\' | while read IP NM; do nc -zw 3 $IP 2222 2>&1 | sed -e "s/.*\($IP\).*/\1/" & done; wait'));
}

if(array_key_exists('STOP',$_REQUEST)) 
  stop_play();

//if user submitted track(s) to play, refresh to music monitor after playback starts
$tracklist=tempnam('/tmp/','tracks');
$thetracks=array();
if(array_key_exists('TRACK',$_REQUEST)) {
  foreach($_REQUEST['TRACK'] as $fn)
    $thetracks[]=$base . urldecode($fn) . "\n";
  $copyFiles=false;
  if(array_key_exists('DEST',$_REQUEST)) {
    if($_REQUEST['DEST'] !== "dsp") {
      $copyFiles=true;
      foreach($thetracks as $track) {
        $fldr=basename(dirname($track)) . '/';
	if($fldr == "Music/") $fldr='';
        system('/usr/local/bin/rsync --chmod=ugo=rwX --inplace -rLptgDe "ssh -l root -i /usr/local/www/apache24/cgi-data/.ssh/id_dsa -o StrictHostKeyChecking=no -p 2222" "' . rtrim($track) . '" ' . $_REQUEST['DEST'] . ':"/mnt/sdcard/Music/' . $fldr . '"&');
      }
    }
  }
  if(!$copyFiles) {
    echo "<!--meta http-equiv='Refresh' content='1; url=/cgi-bin/monitor'-->\n";
    stop_play();
    file_put_contents($tracklist,$thetracks);
    system("/usr/local/bin/mpg123 " . (array_key_exists('SHUFFLE',$_REQUEST) ? $_REQUEST['SHUFFLE'] : "") . " -@ " . $tracklist . " > /tmp/mpg123.log 2>&1 &");
  }
}

?>
</HEAD>
<BODY>
<FONT SIZE='1'>
<!--OL>
<?php
foreach($_POST as $name=>$value) 
   if(is_array($value))
     foreach($value as $track) {
       echo "<LI><B>" . $name . ":</B>" . $track . "\n";
     }
   else
     echo "<LI><B>" . $name . ":</B>" . $value . "\n";

?>
</OL-->

<FORM METHOD='POST'>

<?php
  $stopbanner=false;
  foreach(preg_split('/[\n]/',shell_exec('pgrep mpg123')) as $pid) 
    if($pid !== '') {
      echo "<!--" . $pid . "-->\n";
      if(!$stopbanner) {
        echo "Stop mpg123 process:<BR>\n";
        $stopbanner=true;
      }
      echo shell_exec('ps wwaux | grep -v grep | grep ' . $pid) . "<BR>\n";
      echo shell_exec('ps wwaux | grep -v grep | grep ' . $pid . ' | cut -d " " -f 6');
      echo "<BR><INPUT TYPE='SUBMIT' NAME='STOP' VALUE='" . $pid . "'><BR>\n";
    }

  if(array_key_exists('FILTER',$_REQUEST) && $_REQUEST['FILTER'] !== '') {
    echo "Pick tracks to play, use shift or ctrl to select multiple items<BR>\n";
    echo "<SELECT NAME='TRACK[]' MULTIPLE SIZE='20'>\n";
    $filtersql='';
    $nxtltr='a';
    foreach(preg_split('/[\s,]+/',$_REQUEST['FILTER']) as $value) 
      $filtersql="select filename,shortname from " . ($filtersql == '' ? 'musicfiles ' : "(" . $filtersql . ") ") . $nxtltr++ . " where filename like '%" . $value . "%'"; 
    echo "<!--" . $filtersql . "-->\n";
    foreach($mysql->query($filtersql . " order by 2") as $row)
      echo "<OPTION VALUE='" . $row[0] . "'> " . $row[1] . "\n";

    echo "</SELECT><BR>\n";
    echo "<INPUT TYPE='CHECKBOX' NAME='SHUFFLE' VALUE='-z' CHECKED> Shuffle tracks<BR>\n";
    echo "<SELECT NAME='DEST'>\n";
    echo " <OPTION VALUE='dsp'>Play music now</OPTION>\n";
    foreach(get_devices() as $host => $IPADDR) 
      if($IPADDR !== '') {
        echo " <OPTION VALUE='" . $IPADDR . "'" . (array_key_exists('DEST',$_REQUEST) && $_REQUEST['DEST'] == $IPADDR ? " SELECTED" : "" ) . ">Push file to " . $host;
        echo "</OPTION>\n";
      }
    echo "</SELECT><BR>\n";
  }
?>
Filter track list<BR>
<INPUT TYPE='TEXT' NAME='FILTER' VALUE='<?php if(array_key_exists('FILTER',$_REQUEST)) echo $_REQUEST['FILTER']; ?>'><BR>
<INPUT TYPE='SUBMIT' NAME='MANUEL' VALUE='Go'>
</FORM>
</FONT>
</BODY></HTML>
