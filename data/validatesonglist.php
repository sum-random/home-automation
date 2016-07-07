<?php

include("inc/pdo.php");

include("inc/functions.php");

global $mysql,$log,$base;
$log="/usr/local/www/apache24/cgi-data/musicfiles.log";
$base="/usr/local/media";

write_log("Validate music files");

$selqry="SELECT fileid, filename, inode, size, checksum FROM musicfiles ORDER BY 1";
foreach($mysql->query($selqry) as $row) {
    $fname=$base . '/' . urldecode($row[1]);
    if(file_exists($fname)) {
      write_log("Found: " . $row[0]);
      $fstat=stat($fname);
      if(strlen($row[4]) == 0 ||  $fstat[1] !== $row[2] || $fstat[7] !== $row[3]) { //checksum not present or change in size or location
        $checksum=md5_file($fname);
        sqlupdate("UPDATE musicfiles SET checksum='" . $checksum . "',inode=" . $fstat[1] . ", size=" . $fstat[7] . " WHERE fileid=" . $row[0]);
      }
    } else {
      write_log("Lost: " . $row[1]);
      sqlupdate("DELETE FROM musicfiles WHERE fileid=" . $row[0]);
    }
}

?>

