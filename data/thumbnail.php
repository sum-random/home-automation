<?php

include("generatethumbs.php");

global $mysql,$log;

proc_nice(1);

$base="/usr/local/media/Image";

$thefile=$base . "/NathansWallpaper.JPG";
if(array_key_exists('IMGID',$_REQUEST)) {
  $query="SELECT fname, imgid FROM thumblist WHERE imgid=" . $_REQUEST['IMGID'];
  foreach($mysql->query($query) as $row) {
      $thefile=$row[0];
      $imgid=$row[1];
    }
} else if(array_key_exists('IMG',$_REQUEST)) {
  $query="SELECT fname, imgid FROM thumblist WHERE fname like '%" . $_REQUEST['IMG'] . "%'";
  foreach($mysql->query($query) as $row) {
      $thefile=$row[0];
      $imgid=$row[1];
    }
} else if(array_key_exists('COLLAGEQUERY',$_REQUEST)) {
  $row=matchImage($_REQUEST['COLLAGEQUERY']);
  $thefile=$row[0];
  $imgid=$row[1];
}
//if(isset($query)) 
//  error_log(datestamp() . "Query was " . $query . "\n",3, $log);
//error_log(datestamp() . "File to open is " . $thefile . "\n",3, $log);
$pic=new Imagick();

$cached=false;
$size = (array_key_exists('SIZE',$_REQUEST) ? $_REQUEST['SIZE'] : "scaled64");
foreach($mysql->query("SELECT b.fname, a.imgdata, b.imgid FROM imgcache a INNER JOIN thumblist b ON a.imgid=b.imgid WHERE b.fname='" . $thefile . "' AND a.size='" . $size . "'") as $row) {
  try {
    $pic->clear();
    $pic->readImageBlob(base64_decode($row[1]));
    error_log(datestamp() . "Cache load " . $row[0] . " " . $size . "\n",3, $log);
    $cached=true;
  } catch(Exception $e) {
    sqlquery("DELETE FROM imgcache WHERE imgid=" . $row['imgid']);
    error_log(datestamp() . "Image " . $thefile . " cache problem: " . $size . " with error " . $e->getMessage() . "\n",3,$log);
    $cached=false;
  }
}
if(! $cached) {
  $pic->clear();
  $pic->readImage($thefile);

  try {
    if(array_key_exists('NEWFORMAT',$_REQUEST)) {
      $pic->setImageFormat($_REQUEST['NEWFORMAT']);
    } else
      $pic->setImageFormat('jpg');
  } catch(Exception $e) {
      error_log(datestamp() . "Image " . $thefile . " format problem: " . $_REQUEST['NEWFORMAT'] . " with error " . $e->getMessage() . "\n",3,$log);
  }

  $ph=$pic->getImageHeight();
  $pw=$pic->getImageWidth();
  if(array_key_exists('SIZE',$_REQUEST)) {
    if($size != 'FULL') {
      if(stripos($size,'x') === false) 
        $pic->scaleimage($size,$size,true);
      else {
        $dimensions=explode('x',$size);
        $pic->scaleimage($dimensions[0],$dimensions[1],false);
      }
    } else $cached=true;	//prevent cache insert for full size
  } else if($ph > $pw) {
    $ratio=64/$ph;
    $pic->scaleimage(64,64,true);
  } else {
    $ratio=64/$pw;
    $pic->scaleimage(64,64,true);
  }
}
if(! $cached) {
  $pic->setImageFormat('jpg');
  autoRotateImage($pic);
  $query="INSERT INTO imgcache(imgid,size,imgdata) VALUES( ? , ? , ? )";
  $stmt = $mysql->prepare($query);
  $rowcount = $stmt->execute(array($imgid,$size,base64_encode($pic->getImageBlob())));
  error_log(datestamp() . "Inserted " . $rowcount . " rows " . $thefile . " " . $size . "\n",3, $log);
}
header('Content-Type: image/'.$pic->getImageFormat());
echo $pic;
?>
