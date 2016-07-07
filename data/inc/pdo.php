<?php

define('DATABASE_NAME', '*db_name*');
define('DATABASE_USER', '*db_login*');
define('DATABASE_PASS', '*db_password*');
define('DATABASE_HOST', '*db_host*');

global $mysql,$dblog;

$dblog="/usr/local/www/apache24/cgi-data/db.log";
$mysql = new PDO('mysql:host=' . DATABASE_HOST . ';dbname=' . DATABASE_NAME . ';charset=utf8', DATABASE_USER,DATABASE_PASS);

$mysql->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

function reopendb() {
  $mysql = new PDO('mysql:host=' . DATABASE_HOST . ';dbname=' . DATABASE_NAME . ';charset=utf8', DATABASE_USER,DATABASE_PASS);
}

function dbdatestamp() {
  return date("Ymd H:i:s ",time());
}

function write_db_log($dblogentry) {
  global $dblog;
  if(is_array($dblogentry))
    foreach($dblogentry as $key=>$value)
      error_log(dbdatestamp() . $key . ":" . $value . "\n",3,$dblog);
  else
    error_log(dbdatestamp() . $dblogentry . "\n",3,$dblog);
}

function sqlupdate($query) {
  global $mysql;
  try {
    $rowcount = $mysql->query($query);
    return $rowcount;
  } catch (PDOException $ex) {
    write_db_log('Query failure: ' . $query . ' with error ' . $ex);
  }
  return false;
}

function sqlquery($query) {
  global $mysql;
  $retval=array();
  try {
    foreach($mysql->query($query) as $row) 
      $retval[] = $row;
  } catch (PDOException $ex) {
    write_db_log('Query failure: ' . $query . ' with error ' . $ex);
    return false;
  }
  return $retval;
}

 ?>
