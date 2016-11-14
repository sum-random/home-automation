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
<?php
    if(array_key_exists('SLIDESHOW',$_REQUEST)) {
      $_REQUEST['IMG']=$_REQUEST['SLIDEIMG'];
?>
  <script type="text/javascript" >
    var myVar = setInterval(pushButton,5000);
    function pushButton() { document.forms[0].submit(); }
  </script>
<?php
    }
?>
</HEAD>
<BODY>
<DIV ID='POPWIN' STYLE='position:absolute;visibility:hidden;'> </DIV>
<FORM METHOD='POST'>
<?php
set_time_limit(300);
$noscanimages=true;
include("generatethumbs.php");

global $mysql;

$mypid=getmypid();
$mynice=shell_exec("ps -auxo nice | grep -v grep | grep " . $mypid . " | awk '{print $12}'");
if($mynice < 10)
  proc_nice(1);

$base='/storage/Image';
$setlist=preg_split('/\n/',shell_exec("find " . $base . " -type d -maxdepth 1 | cut -d / -f 4- | sort"));

if(! array_key_exists('SET',$_REQUEST)) {
  //$_REQUEST['SET']=$setlist[0];
  foreach($setlist as $fldr)
    if(preg_match('/nathan/',$fldr))
      $_REQUEST['SET']=$fldr;
}

$scanDir=$base . '/' . $_REQUEST['SET'] ;

if(array_key_exists('OPTION',$_REQUEST)) 
  echo "<INPUT ID='OPTION' TYPE='HIDDEN' NAME='OPTION' VALUE='" . $_REQUEST['OPTION'] . "'>\n";

function inImageDb($fileName) {
  $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fileName . "'");
  //echo "<!--\n";
  //print_r($retval);
  //echo "$fileName \n";
  //echo "-->\n";
  return (count($retval) > 0) ;
}

function getIdForImage($fname) {
  $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fname . "'");
  if(count($retval) == 0) {
    $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='/" . $fname . "'");
    if(count($retval) > 0) {
      sqlquery("UPDATE thumblist SET fname='" . $fname . "' WHERE imgid=" . $retval[0][0] ); $retval=sqlquery("SELECT imgid FROM thumblist WHERE fname='" . $fname . "'"); } else $retval=registerImage($fname, true); shell_exec("php rescanimage '" . $fname . "' & "); return $retval; }
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

$page=0;
if(array_key_exists('page',$_REQUEST)) 
  $page=$_REQUEST['page'];
if(array_key_exists('newpage',$_REQUEST)) 
  foreach(($_REQUEST['newpage']) as $idx=>$val)
    $page=$idx;
echo "<!--SELECT fname,imgid FROM thumblist WHERE fname like '" . $scanDir . "%' order by 1 DESC-->";
$imglist=sqlquery("SELECT fname,imgid FROM thumblist WHERE fname like '" . $scanDir . "%' order by 1 DESC");
if($page * 100 > count($imglist)) 
  $page=intval(count($imglist) / 100);
echo "<INPUT TYPE='HIDDEN' NAME='page' VALUE='" . $page . "'>\n";

if(array_key_exists('IMG',$_REQUEST) && is_array($_REQUEST['IMG']) && ! array_key_exists('HOME',$_REQUEST)) {
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
  $imgidx=-1;
  $min=0;
  $max=count($imglist);
  while($imgidx == -1 && $max >= $min) { 
    $mid=intval(($max+$min) / 2);
    $midname=$imglist[$mid]['fname'];
    write_log("Searching " . basename($theImage) . " found " . basename($midname) . "\t" . $min . " " . $mid . " " . $max);
    $cmpval=strcmp($theImage,$midname);
    if($cmpval == 0)
      $imgidx=$mid;
    else if($cmpval < 0)
      $min=$mid + 1;
    else
      $max=$mid - 1;
  }
  if($imgidx !== -1) {
    $firstidx=$page * 100;
    $firstid=$imglist[$firstidx]['imgid'];
    $theid=$imglist[$imgidx]['imgid'];
    $nxtidx=($imgidx - 1 <= $firstidx ? $firstidx : $imgidx - 1);
    $nxtid=$imglist[$nxtidx]['imgid'];
    $lastidx=($page * 100 + 99 >= count($imglist) ? count($imglist) - 1 : $page * 100 + 99);
    $lastid=$imglist[$lastidx]['imgid'];
    $prvidx=($imgidx + 1 > $lastidx ? $lastidx : $imgidx + 1);
    $prvid=$imglist[$prvidx]['imgid'];
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='First' TYPE='IMAGE' NAME='IMG[" . $firstid . "]' SRC='thumbnail.php?IMGID=" . $firstid . "&SIZE=80'></TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='Next' TYPE='IMAGE' NAME='IMG[" . $nxtid . "]' SRC='thumbnail.php?IMGID=" . $nxtid . "&SIZE=80'></TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><A HREF='collage.php?IMGID=" . getIdForImage($theImage) . "&SCALE=640&THUMBSZ=64' TITLE='Collage'><IMG ALT='Collage' SRC='/img/collage.jpg'></A></TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ALT='Index' TYPE='IMAGE' NAME='HOME' VALUE='GO THERE' SRC='/img/btn_up.jpg'></TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'>";
    if(array_key_exists('SLIDESHOW',$_REQUEST) && $firstidx != $imgidx) {
      echo "<INPUT TYPE='HIDDEN' NAME='SLIDEIMG[" . $nxtid . "]' VALUE=''>\n";
      echo "<INPUT TYPE='HIDDEN' NAME='SLIDESHOW[" .  $_REQUEST['SET'] . "]' VALUE=''>\n";
    } else {
      echo "<INPUT TYPE='HIDDEN' NAME='SLIDEIMG[" . $imglist[$imgidx]['imgid'] . "]' VALUE=''>\n";
      echo "<INPUT ALT='Slideshow' TYPE='IMAGE' NAME='SLIDESHOW[" .  $_REQUEST['SET'] . "]' SRC='/img/projector.GIF'>";
    }
    echo "</TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='Previous' TYPE='IMAGE' NAME='IMG[" . $prvid . "]' SRC='thumbnail.php?IMGID=" . $prvid . "&SIZE=80'></TD>\n";
    echo "<TD VALIGN='TOP' ALIGN='CENTER'><INPUT ID='IMGCELL' ALT='Last' TYPE='IMAGE' NAME='IMG[" . $lastid . "]' SRC='thumbnail.php?IMGID=" . $lastid . "&SIZE=80'></TD>\n";
  }
  echo "</TR></TABLE>\n";
} else {
    echo "<SELECT NAME='SET' onChange='submit();'>\n";
    foreach($setlist as $fldr)
      if(strpos($fldr,'.') == false)
        echo "<OPTION " . ($fldr == $_REQUEST['SET'] ? " SELECTED " : "" ) . "VALUE='" . $fldr . "'>" . $fldr . "</OPTION>\n";
    echo "</SELECT><BR>\n";
    if($page > 0) {
      echo "<INPUT ID='NAVCELL' TYPE='IMAGE' ALT='/thumbnail.php?IMGID=" . $imglist[($page - 1) * 100]['imgid'] . "' NAME='newpage[0]' VALUE='";
      echo $page - 1 . "' SRC='/img/btn_lt.jpg'>\n";
    }
    for($idx  = 0; $idx <= count($imglist) / 100; $idx++) 
      if($idx == $page)
        echo $page;
      else
        echo "<INPUT ID='NAVCELL' TYPE='IMAGE' ALT='/thumbnail.php?IMGID=" . $imglist[$idx * 100]['imgid'] . "' NAME='newpage[" . $idx . "]' VALUE='" . $idx . "' SRC='/img/btn_" . ($idx > $page ? "r" : "l") . "t.jpg'>\n";
    if($page + 1 < (count($imglist) / 100)) {
      echo "<INPUT ID='NAVCELL' TYPE='IMAGE' ALT='/thumblist.php?IMGID=" . $imglist[($page + 1) * 100]['imgid'] . "' NAME='newpage[";
      echo $page + 1 . "]' VALUE='";
      echo $page + 1 . "' SRC='/img/btn_rt.jpg'>\n";
    }
    echo "<BR>\n";
    for($idx  = $page * 100; $idx <= $page * 100 + 99 && $idx < count($imglist); $idx++) {
      $file = $imglist[$idx]['fname'];
      if(inImageDb($file) || isImage($file)) {
        $imgID=$imglist[$idx]['imgid'];
        echo "<INPUT TYPE='IMAGE' ID='IMGCELL' NAME='IMG[" . $imgID . "]' VALUE='" . basename($file) . "' SRC='/thumbnail.php?IMGID=" . $imgID . "&SIZE=64'>\n";
      }
    } 
}

?>
</FORM>
</BODY></HTML>

