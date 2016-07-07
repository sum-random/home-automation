<?php

define('DATABASE_NAME', '*db_name*');
define('DATABASE_USER', '*db_login*');
define('DATABASE_PASS', '*db_password*');
define('DATABASE_HOST', '*db_host*');

global $mysql,$dblog;

$dblog="/usr/local/www/apache24/cgi-data/db.log";
$mysql=mysql_connect(DATABASE_HOST,DATABASE_USER,DATABASE_PASS,false);
mysql_select_db(DATABASE_NAME,$mysql);

function reopendb() {
  $mysql=mysql_connect(DATABASE_HOST,DATABASE_USER,DATABASE_PASS,true);
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
  if(! mysql_query($query,$mysql)) {
    write_db_log('Query failure: ' . $query . ' with error ' . mysql_error());
    return false;
  } else
    return true;
}

function sqlquery($query) {
  global $mysql;
  $retval=array();
  if($result=mysql_query($query,$mysql)) {
    while($row=mysql_fetch_array($result))
      $retval[]=$row;
    mysql_free_result($result);
  } else {
    write_db_log('Query failure: ' . $query . ' with error ' . mysql_error());
    return false;
  }
  return $retval;
}

 ?>
