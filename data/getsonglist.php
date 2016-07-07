<?php

include("inc/pdo.php");

$log="/usr/local/www/apache24/cgi-data/musicfiles.log";

global $mysql,$base;
if($argc == 1)
  $base="/usr/local/media";
else
  $base=$argv[1];

foreach(preg_split('/[\n]/',shell_exec('nice -n 20 find ' . $base . ' -type f -name "*[mM][pP]3" | cut -d / -f 5-')) as $fname) {
  if(strlen($fname) > 0) {
    $fldr=dirname($fname);
    $parent=urlencode(basename($fldr));
    $thefile=urlencode(basename($fname));
    $urlenc=urlencode($fname);
    $find="SELECT count(*) FROM musicfiles WHERE filename='" . $urlenc . "'";
    $ins="INSERT INTO musicfiles (filename,shortname) VALUES ('" . $urlenc . "','" . $parent . " - " . $thefile . "');";
    foreach($mysql->query($find) as $fcnt) {
      if($fcnt[0] === 0) {
        $mysql->query($ins);
      } else { 
        error_log("Found: " . $find . ' :: ',3,$log);
      }
    }
  }
}

?>

