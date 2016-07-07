<?php
include("generatethumbs.php");
  if(count($argv) == 2 && is_file($argv[1]) && isImage($argv[1])) {
    registerImage($argv[1]);
  }
?>
