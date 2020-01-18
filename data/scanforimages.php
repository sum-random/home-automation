<?php

include("generatethumbs.php");

global $mysql;

$base="/storage/Image/nathan12";
$pic=new Imagick();

  try {
    write_log("Fixup thumblist");
    foreach($mysql->query("select fname from thumblist where llb=-1") as $row) {
      echo ":" . $row['fname'] . ":\n";
      registerImage($row['fname']);
    }
    write_log("Cleanup deleted");
    foreach($mysql->query("SELECT fname,imgid FROM thumblist") as $row) 
      if( ! file_exists($row['fname'])) {
        $mysql->query("DELETE FROM imgcache WHERE imgid=" . $row['imgid']);
        $mysql->query("DELETE FROM thumblist WHERE imgid=" . $row['imgid']);
      }

    write_log("Scan for new files");
    foreach(preg_split('/[\n]/',shell_exec("nice -n 20 find " . $base . " -type f | grep -iE 'jpg$|gif$|jpeg$|png$|tiff$|ico$' | sort -r")) as $fname) {
      write_log("Checking " . $fname);
      $query = "SELECT COUNT(*) FROM thumblist WHERE fname='" . $fname . "'";
      //write_log($query);
      foreach($mysql->query($query) as $cntrow) 
        if($cntrow[0] == 0)
          registerImage($fname);
        else 
          write_log("Already registered - " . $fname);
      foreach($mysql->query("SELECT fname,imgid FROM thumblist WHERE fname='" . $fname . "'") as $row) 
        foreach(array("64","480","16x16","24x24","32x32","64x64") as $size) {
          write_log("Check thumbnail " . $row['imgid'] . " " . $size);
          $query = "SELECT count(*) as present FROM imgcache WHERE size='" . $size . "' AND imgid=" . $row['imgid'];
          //write_log($query);
          foreach($mysql->query($query) as $cached)
            if($cached['present'] == 0) {
                  try {
                    $pic->clear();
                    $pic->readImage($row['fname']);
                    autoRotateImage($pic);
                    if(stripos($size,'x') === false) 
                      $pic->scaleimage($size,$size,true);
                    else {
                      $dimensions=explode('x',$size);
                      $pic->scaleimage($dimensions[0],$dimensions[1],false);
                    }
                    cacheWriteImage($row['imgid'],$size,$pic);
                  } catch(Exception $e) {
                    write_log("Caught exception: " . $e->getmessage());
                  }
            } else 
              write_log("Already cached - " . $row['fname'] . " " . $size);
        }
    }
  } catch(PDOException $e) {
    write_log("Caught exception: " . $e->getmessage());
  }

?>
