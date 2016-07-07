<?php

include("inc/pdo.php");
include("inc/functions.php");

global $mysql;
$base="/usr/local/media";

$handle=popen('nice -n 20 find ' . $base . ' -type f -size +1M | grep -v .snap | cut -d / -f 5-','r');
while($fname=str_replace("\n",'',fgets($handle))) {
  $full=$base . '/' . $fname;
  $update=false;
  $insert=false;
  $fstat=stat($full);
  $query="SELECT count(*) FROM crosslinks WHERE fname='" . $fname . "'";
  foreach($mysql->query($query) as $frow) {
    if($frow[0] == 0) {
      $mysql->query("UPDATE crosslinks SET inode=" . $fstat['ino'] . ", size=" . $fstat['size'] . ", md5='" . md5_file($full) . "' WHERE fname=" . $fname);
    } else {
      $mysql->query("INSERT INTO crosslinks(fname, inode, size, md5) VALUES ('" . $fname . "'," . $fstat['ino'] . "," . $fstat['size'] . ",'" . md5_file($full) . "')");
    }
  }
}
?>
