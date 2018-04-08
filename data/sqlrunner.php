<?php

header('Content-type: text/csv');
header('Content-disposition: attachment;filename=MyVerySpecial.csv');

include("inc/pdo.php");
include("inc/functions.php");

global $mysql;

if(! array_key_exists('SQL',$_REQUEST)) {
  $rounding = -5;
  $_REQUEST['SQL'] = "SELECT ROUND(size, " . $rounding . ") AS filesize, count(*) AS num FROM musicfiles WHERE size>100000 GROUP BY ROUND(size, " . $rounding . ") HAVING count(*)>0;";
}

$needheader = true;
foreach(sqlquery($_REQUEST['SQL']) as $idx=>$val) {
  if($needheader) {
    $needheader=false;
    $sep = "";
    foreach($val as $vi=>$vv)
      if(! is_int($vi)) {
        printf($sep . $vi);
        $sep = ",";
      }
    printf("\n");
  }
  if($val['filesize']>0)
    printf($val['filesize'] . "," . $val['num'] . "\n");
}

?>
