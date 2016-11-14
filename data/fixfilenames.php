<?php
include("generatethumbs.php");
  $query="SELECT fname, imgid FROM thumblist WHERE fname like '/usr/local/media%'";
  foreach($mysql->query($query) as $row) {
      $thefile=$row[0];
      $newName=preg_replace("/usr\/local\/media/","storage",$thefile);
      $imgid=$row[1];
      $mysql->query("UPDATE thumblist SET fname='" . $newName . "' WHERE imgid=" . $imgid );
      printf("%s completed\n",$newName);
    }
?>
