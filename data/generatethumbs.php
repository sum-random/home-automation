<?php

include("inc/pdo.php");
include("inc/functions.php");

$base="/usr/local/media/Image";

function autoRotateImage($image) { 
    $orientation = $image->getImageOrientation(); 

    switch($orientation) { 
        case imagick::ORIENTATION_BOTTOMRIGHT: 
            $image->rotateimage("#000", 180); // rotate 180 degrees 
        break; 

        case imagick::ORIENTATION_RIGHTTOP: 
            $image->rotateimage("#000", 90); // rotate 90 degrees CW 
        break; 

        case imagick::ORIENTATION_LEFTBOTTOM: 
            $image->rotateimage("#000", -90); // rotate 90 degrees CCW 
        break; 
    } 

    // Now that it's auto-rotated, make sure the EXIF data is correct in case the EXIF gets saved with the image! 
    $image->setImageOrientation(imagick::ORIENTATION_TOPLEFT); 
} 

function isImage($fileName) {
  return(strpos(shell_exec("file -i '" . $fileName . "' | cut -d : -f 2") ,'image') !== false);
}

function cacheWriteImage($imgid,$size,$pic) {
  global $mysql,$log;

  $query="INSERT INTO imgcache(imgid,size,imgdata) VALUES( ? , ? , ? )";
  $stmt = $mysql->prepare($query);
  $rowcount = $stmt->execute(array($imgid,$size,base64_encode($pic->getImageBlob())));
  error_log(datestamp() . "Inserted " . $rowcount . " rows " . $imgid . " " . $size . "\n",3, $log);
}

function cacheReadImage($thefile,$size) {
  global $mysql,$log;

  foreach($mysql->query("SELECT b.fname, a.imgdata, b.imgid FROM imgcache a INNER JOIN thumblist b ON a.imgid=b.imgid WHERE b.fname='" . $thefile . "' AND a.size='" . $size . "'") as $row) {
    try {
      $pic->clear();
      $pic->readImageBlob(base64_decode($row[1]));
      error_log(datestamp() . "Cache load " . $row[0] . " " . $size . "\n",3, $log);
      return $pic;
    } catch(Exception $e) {
      sqlquery("DELETE FROM imgcache WHERE imgid=" . $row['imgid']);
      error_log(datestamp() . "Image " . $thefile . " cache problem: " . $size . " with error " . $e->getMessage() . "\n",3,$log);
    }
  }
  return false;
}

function matchImage($qry) {
  global $mysql;
  $colors=preg_split('/:/',$qry);
  $query="SELECT fname,imgid, ABS(ulr-" . $colors[0] . ")+ABS(ulg-" . $colors[1] . ")+ABS(ulb-" . $colors[2] . ")+ABS(urr-" . $colors[3] . ")+ABS(urg-" . $colors[4] . ")+ABS(urb-" . $colors[5] . ")+ABS(llr-" . $colors[6] . ")+ABS(llg-" . $colors[7] . ")+ABS(llb-" . $colors[8] . ")+ABS(lrr-" . $colors[9] . ")+ABS(lrg-" . $colors[10] . ")+ABS(lrb-" . $colors[11] . ") AS score, a.imgid FROM thumblist a WHERE fname LIKE '%jpg' ORDER BY 3 LIMIT 1";
  foreach($mysql->query($query) as $row) {
    return $row;
  }
}

function registerImage($fname, $quick = false) {
  global $mysql;
  if(is_file($fname) && isImage($fname)) {
   try {
    write_log($fname);
    if($quick) {
      $query="INSERT INTO thumblist (fname, urr, urg, urb, ulr, ulg, ulb, lrr, lrg, lrb, llr, llg, llb) VALUES ('" . $fname . "', -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1)";
    } else {
      $pic=new Imagick();

      $pic->clear();
      $pic->readImage($fname);
      $cx=$pic->getImageWidth() / 2;
      $cy=$pic->getImageHeight()/ 2;

      $pic->cropImage($cx,$cy,0,0);
      $urr=$pic->getImageChannelMean(imagick::CHANNEL_RED);
      $urg=$pic->getImageChannelMean(imagick::CHANNEL_GREEN);
      $urb=$pic->getImageChannelMean(imagick::CHANNEL_BLUE);
    
      $pic->clear();
      $pic->readImage($fname);
      $pic->cropImage($cx,$cy,$cx,0);
      $ulr=$pic->getImageChannelMean(imagick::CHANNEL_RED);
      $ulg=$pic->getImageChannelMean(imagick::CHANNEL_GREEN);
      $ulb=$pic->getImageChannelMean(imagick::CHANNEL_BLUE);
  
      $pic->readImage($fname);
      $pic->cropImage($cx,$cy,0,$cy);
      $lrr=$pic->getImageChannelMean(imagick::CHANNEL_RED);
      $lrg=$pic->getImageChannelMean(imagick::CHANNEL_GREEN);
      $lrb=$pic->getImageChannelMean(imagick::CHANNEL_BLUE);
  
      $pic->clear();
      $pic->readImage($fname);
      $pic->cropImage($cx,$cy,$cx,$cy);
      $llr=$pic->getImageChannelMean(imagick::CHANNEL_RED);
      $llg=$pic->getImageChannelMean(imagick::CHANNEL_GREEN);
      $llb=$pic->getImageChannelMean(imagick::CHANNEL_BLUE);

      foreach($mysql->query("SELECT COUNT(*) FROM thumblist WHERE fname='" . $fname . "'") as $cntrow)
        if($cntrow[0] == 1)
          $query="UPDATE thumblist SET urr=" . intval($urr['mean'] / 256) . ",urg=" . intval($urg['mean'] / 256) . ",urb=" . intval($urb['mean'] / 256) . ",ulr=" . intval($ulr['mean'] / 256) . ",ulg=" . intval($ulg['mean'] / 256) . ",ulb=" . intval($ulb['mean'] / 256) . ",lrr=" . intval($lrr['mean'] / 256) . ",lrg=" . intval($lrg['mean'] / 256) . ",lrb=" . intval($lrb['mean'] / 256) . ",llr=" . intval($llr['mean'] / 256) . ",llg=" . intval($llg['mean'] / 256) . ",llb=" . intval($llb['mean'] / 256) . " WHERE fname='" . $fname . "'";
        else
          $query="INSERT INTO thumblist (fname, urr, urg, urb, ulr, ulg, ulb, lrr, lrg, lrb, llr, llg, llb) VALUES ('" . $fname . "', " . intval($urr['mean'] / 256) . "," . intval($urg['mean'] / 256) . "," . intval($urb['mean'] / 256) . "," . intval($ulr['mean'] / 256) . "," . intval($ulg['mean'] / 256) . "," . intval($ulb['mean'] / 256) . "," . intval($lrr['mean'] / 256) . "," . intval($lrg['mean'] / 256) . "," . intval($lrb['mean'] / 256) . "," . intval($llr['mean'] / 256) . "," . intval($llg['mean'] / 256) . "," . intval($llb['mean'] / 256) . ")";
    }

    write_log($query);
    sqlupdate($query);
    foreach($mysql->query("SELECT a.imgid, b.size FROM thumblist a LEFT JOIN imgcache b on a.imgid=b.imgid WHERE a.fname='" . $fname . "' AND b.size='64'") as $row)
        if(strlen($row['size']) == 0) {
          $pic->clear();
          $pic->readImage($fname);
          autoRotateImage($pic);
          $pic->scaleimage(64,64,true);
          cacheWriteImage($row['imgid'],"64",$pic);
        }
   } catch(PDOException $e) {
    write_log("Caught exception: " . $e->getmessage());
   }
  }
  foreach($mysql->query("SELECT imgId FROM thumblist WHERE fname='" . $fname . "'") as $row)
    return $row[0];
  return null;
}

?>
