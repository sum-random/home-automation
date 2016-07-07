<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<HTML><HEAD>
<style>
table, th, tr, td, a {
  border: 0;
  cellpadding: 0px;
  cellspacing: 0px;
  border-spacing: 0px;
  border-collapse: collapse;
  border-image-width: 0px;
  font-size:0.25em;
  vertical-align: middle;
}

img, input {
  vertical-align: middle;
}

</style>
<TITLE>Picture viewer</TITLE>
<script type="text/javascript" src="/jscript/pix.php.js"></script>
</HEAD>
<BODY>
<DIV ID='POPWIN' STYLE='position:absolute;visibility:hidden;'> </DIV>
<FORM METHOD='POST'>
<?php
set_time_limit(300);
$noscanimages=true;
$imgFilter="jpg$|jpeg$|gif$|png$";
include("generatethumbs.php");

global $mysql;

$mypid=getmypid();
$mynice=shell_exec("ps -auxo nice | grep -v grep | grep " . $mypid . " | awk '{print $12}'");
if($mynice < 10)
  proc_nice(1);

$base='/usr/local/media/Image';

if(! array_key_exists('SET',$_REQUEST)) {
  $_REQUEST['SET']='';
}

if(array_key_exists('OPTION',$_REQUEST)) 
  echo "<INPUT ID='OPTION' TYPE='HIDDEN' NAME='OPTION' VALUE='" . $_REQUEST['OPTION'] . "'>\n";

function inImageDb($fileName) {
  $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fileName . "'");
  echo "<!--\n";
  print_r($retval);
  echo "$fileName \n";
  echo "-->\n";
  return (count($retval) > 0) ;
}

function getIdForImage($fname) {
  $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fname . "'");
  if(count($retval) == 0) {
    $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='/" . $fname . "'");
    if(count($retval) > 0) {
      sqlquery("UPDATE thumblist SET fname='" . $fname . "' WHERE imgid=" . $retval[0][0] );
      $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fname . "'");
    } else 
      $retval=registerImage($fname, true);
      shell_exec("php rescanimage '" . $fname . "' & ");
      return $retval;
  }
  echo "<!--\n";
  print_r($retval);
  echo "$fname \n";
  echo "-->\n";
  return $retval[0][0];
}

function rotateImage($imgId, $degree) {
  sqlquery("DELETE FROM imgcache WHERE imgid=" . $imgId);
  $imgName=sqlquery("SELECT fname FROM thumblist WHERE imgid=" . $imgId)[0][0];
  $pic=new Imagick();
  $pic->clear();
  $pic->readImage($imgName);
  $pic->rotateImage(new ImagickPixel('none'),$degree);
  $pic->writeImage($imgName);
  $pic->clear();
  $pic->destroy();
}

//print_r($_REQUEST);

if(! array_key_exists('SET',$_REQUEST))
  $_REQUEST['SET']='20140410';

if(array_key_exists('IMG',$_REQUEST) && is_array($_REQUEST['IMG'])) {
  echo "<INPUT TYPE='HIDDEN' NAME='SET' VALUE='" . $_REQUEST['SET'] . "'>\n";
  $img=(array_keys($_REQUEST['IMG'])[0]);
  switch($_REQUEST['IMG'][$img]) {
    case "RIGHT" :
      rotateImage($img,90);
      break;
    case "LEFT" :
      rotateImage($img,-90);
      break;
    default :
      break;
  }
  $theImage=sqlquery("SELECT fname FROM thumblist WHERE imgid=" . $img)[0][0];
  echo "<CENTER><TABLE BORDER='0'><TR><TD><BUTTON TYPE='SUBMIT' NAME='IMG[" . $img . "]' ALT='Rotate left' VALUE='LEFT'><IMG SRC='/img/rotate_l.png'></BUTTON></TD>";
  echo "<TD ALIGN='CENTER' COLSPAN='5'><A HREF='thumbnail.php?IMGID=" . $img . "&SIZE=FULL' TITLE='Full resolution'><IMG SRC='thumbnail.php?IMGID=" . $img . "&SIZE=640'></A></TD>";
  echo "<TD><BUTTON TYPE='SUBMIT' NAME='IMG[" . $img . "]' ALT='Rotate right' VALUE='RIGHT'><IMG SRC='/img/rotate_r.png' ></BUTTON></TD></TR>\n";
  echo "<TR>";
  $first=true;
  $atimage=false;
  $prev=$theImage;
  $lastImage=$theImage;
  foreach(preg_split('/\n/',shell_exec("find " . dirname($theImage) . " -type f -maxdepth 1 | grep -iE '" . $imgFilter . "' | sort -r")) as $file) {
    if(inImageDb($file) || isImage($file)) {
      write_log("File name is " . $file);
      if($first) {
        write_log($theImage . " First = " . $file);
        $first=false;
        $prev=$file;
        $imgid=getIdForImage($file);
        echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='First' TYPE='IMAGE' NAME='IMG[" . $imgid . "]' SRC='thumbnail.php?IMGID=" . $imgid . "&SIZE=80'></TD>\n";
      }
      if($atimage) {
        write_log($theImage . " after image = " . $file);
        $atimage=false;
        $afterImage=$file;
      }
      if($file == $theImage) {
        write_log($theImage . " at image prev = " . $prev);
        $previd=getIdForImage($prev);
        echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='Previous' TYPE='IMAGE' NAME='IMG[" . $previd . "]' SRC='thumbnail.php?IMGID=" . $previd . "&SIZE=80'></TD>\n";
        echo "<TD VALIGN='TOP' ALIGN='CENTER'><A HREF='collage.php?IMGID=" . getIdForImage($theImage) . "&SCALE=640&THUMBSZ=64' TITLE='Collage'><IMG ALT='Collage' SRC='/img/collage.jpg'></A></TD>\n";
        echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ALT='Index' TYPE='IMAGE' NAME='HOME' VALUE='GO THERE' SRC='/img/btn_up.jpg'></TD>\n";
        echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ALT='Slideshow' TYPE='IMAGE' NAME='SLIDESHOW[" .  $_REQUEST['SET'] . "]' SRC='/img/projector.GIF'></TD>\n";
        $atimage=true;
        $afterImage=$file;
      }
      $lastImage=$file;
      $prev=$file;
    }
  }
  $nxtid=getIdForImage($afterImage);
  echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='Next' TYPE='IMAGE' NAME='IMG[" . $nxtid . "]' SRC='thumbnail.php?IMGID=" . $nxtid . "&SIZE=80'></TD>\n";
  $lastid=getIdForImage($lastImage);
  echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ALT='Last' ID='IMGCELL' TYPE='IMAGE' NAME='IMG[" . $lastid . "]' SRC='thumbnail.php?IMGID=" . $lastid . "&SIZE=80'></TD>\n";
  echo "</TR></TABLE>\n";
      

} else {
    if(array_key_exists('page',$_REQUEST)) $page=$_REQUEST['page'];
    else $page=0;
    echo "<SELECT NAME='SET' onChange='submit();'>\n";
    foreach(preg_split('/\n/',shell_exec("find " . $base . " -type d -maxdepth 1 | cut -d / -f 6- | sort")) as $fldr)
      if(strpos($fldr,'.') == false)
        echo "<OPTION " . ($fldr == $_REQUEST['SET'] ? " SELECTED " : "" ) . "VALUE='" . $fldr . "'>" . $fldr . "</OPTION>\n";
    echo "</SELECT><BR>\n";
    $scanDir=$base . '/' . $_REQUEST['SET'] ;
    $files=preg_split('/\n/',shell_exec("find " . $scanDir . " -type f | grep -iE '" . $imgFilter . "' | sort -r"));
    echo "<!--scanDir=" . $scanDir . "<BR-->\n";
    if($page > 0) {
      echo "<INPUT TYPE='IMAGE' ALT='Back' NAME='page' VALUE='";
      echo $page - 1 . "' SRC='/img/btn_lt.jpg'>\n";
    }
    for($idx  = 0; $idx <= count($files) / 100; $idx++) 
      if($idx == $page)
        echo $page;
      else
        echo "<INPUT TYPE='IMAGE' ALT='Page " . $idx . "' NAME='page' VALUE='" . $idx . "' SRC='/img/btn_" . ($idx > $page ? "r" : "l") . "t.jpg'>\n";
    if($page + 1 < (count($files) / 100)) {
      echo "<INPUT TYPE='IMAGE' ALT='Fwd' NAME='page' VALUE='";
      echo $page + 1 . "' SRC='/img/btn_rt.jpg'>\n";
    }
    echo "<BR>\n";
    for($idx  = $page * 100; $idx < $page * 100 + 100 && $idx < count($files); $idx++) {
      $file = $files[$idx];
      echo "<!-- " . $scanDir . "-->\n";
      if(inImageDb($file) || isImage($file)) {
        $imgID=getIdForImage($file);
        echo "<INPUT TYPE='IMAGE' ID='IMGCELL' NAME='IMG[" . $imgID . "]' VALUE='" . basename($file) . "' SRC='/thumbnail.php?IMGID=" . $imgID . "&SIZE=64'>\n";
        usleep(100);
      }
    } 
}

?>
</FORM>
</BODY></HTML>

