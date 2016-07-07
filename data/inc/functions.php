<?php

global $log,$mysem;
$log='/usr/local/www/apache24/cgi-data/php.log';

function datestamp() {
  return date("Ymd H:i:s ",time());
}

function write_log($logentry) {
  global $log;
  if(is_array($logentry))
    foreach($logentry as $key=>$value)
      error_log(datestamp() . $key . ":" . $value . "\n",3,$log);
  else
    error_log(datestamp() . $logentry . "\n",3,$log);
}

//$mysem=sem_get(ftok('/COPYRIGHT'));

function lightControl($house,$light,$state) {
  global $mysem;

  sem_acquire($mysem);

  shell_exec("/usr/local/bin/br -x /dev/cuau0 -c " . $house . " -r 2 "  . ($state ? "-n" : "-f") . " " . $light);

  sem_release($mysem);
}

?>
