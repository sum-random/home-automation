<!DOCTYPE html>
<HTML>
<HEAD>
<TITLE><?php array_key_exists('IMG',$_REQUEST) ? $_REQUEST['IMG'] : "No IMG specified" ?></TITLE>
<style>
table, th, tr, td, a {
  border: 0;
  cellpadding: 0px;
  cellspacing: 0px;
  border-spacing: 0px;
  border-collapse: collapse;
  border-image-width: 0px;
  font-size:0.25em;
}

img {
  vertical-align: bottom;
}
</style>
<script type="text/javascript" src="/jscript/collage.js"></script>
</HEAD>
<BODY>
<DIV ID='POPWIN' STYLE='position:absolute;visibility:hidden;'> </DIV>
<FORM>
<?php
include("generatethumbs.php");
global $mysql,$base,$log,$thumbsz,$scaleimg;

function insertCell(&$list, $offset, $colors){
  global $thumbsz,$scaleimg;

  $imgquery=$colors[0];
  $bgcolor=$colors[1];
  $imginfo=matchImage($imgquery);
  $subimgid=$imginfo[1];
  $subimgname=$imginfo[0];
  $imgsrc="thumbnail.php?IMGID=" . $subimgid;
  $list[$offset]="<TD STYLE='background-color: #" . $bgcolor . ";' bgcolor='" . $bgcolor . "'><A TITLE='" . $bgcolor . "' HREF='/collage.php?IMGID=" . $subimgid . "&THUMBSZ=" . $thumbsz . "&SCALE=" . $scaleimg . "' BORDER='0' ><IMG ID='IMGCELL' onMouseOver='showPreview();' onMouseOut='hidePreview();' BORDER='0' ALT='" . $imgquery . "' SRC='" . $imgsrc . "&SIZE=" . $thumbsz . "x" . $thumbsz . "' HEIGHT='" . $thumbsz . "' WIDTH='" . $thumbsz . "'></A></TD>\n";
  echo "<!-- $offset $bgcolor :" . $list[$offset] . ":-->\n";
}


if(array_key_exists('IMGID',$_REQUEST)) {
  foreach($mysql->query("SELECT fname,imgid FROM thumblist WHERE imgid=" . $_REQUEST['IMGID']) as $row) 
    if(file_exists($row[0])) {
      $srcfname=$row[0];
      $srcimgid=$row[1];
    }
} else if(array_key_exists('IMGMATCH',$_REQUEST)) {
  $row=matchImage($_REQUEST['IMGMATCH']);
    if(file_exists($row[0])) { 
      $srcfname=$row[0];
      $srcimgid=$row[1];
    }
} else {
  echo "Missing IMG";
  exit(1);
}

      $pic=new Imagick();
      $pic->clear();
      $pic->readImage($srcfname);
      //$pic->setImageFormat('png');
      autoRotateImage($pic);

      $ph=$pic->getImageHeight();
      $pw=$pic->getImageWidth();

      $thumbsz=96;
      $scaleimg=640;
      if(array_key_exists('THUMBSZ',$_REQUEST))
        $thumbsz=$_REQUEST['THUMBSZ'];
      if(array_key_exists('SCALE',$_REQUEST))
        $scaleimg=$_REQUEST['SCALE'];

      if(array_key_exists('IMGID',$_REQUEST)) 
        echo "<INPUT TYPE='HIDDEN' NAME='IMGID' VALUE='" . $_REQUEST['IMGID'] . "'>\n";
      if(array_key_exists('IMGMATCH',$_REQUEST)) 
        echo "<INPUT TYPE='HIDDEN' NAME='IMGMATCH' VALUE='" . $_REQUEST['IMGMATCH'] . "'>\n";
      echo "Thumbnail size: <SELECT NAME='THUMBSZ' onChange='submit();'>\n";
      foreach(array(4,8,12,16,20,24,28,32,36,40,44,48,56,64,72,80,88,96,112,128) as $nxtthumb)
        echo "<OPTION VALUE=" . $nxtthumb . ($thumbsz == $nxtthumb ? " SELECTED " : "") . ">" . $nxtthumb . "</OPTION>\n";
      echo "</SELECT><BR>\n";
      echo "Output size: <SELECT NAME='SCALE' onChange='submit();'>\n";
      foreach(array(640,800,960,1024,1280,1600,1920) as $nxtsz)
        echo "<OPTION VALUE=" . $nxtsz . ($scaleimg == $nxtsz ? " SELECTED " : "") . ">" . $nxtsz . "</OPTION>\n";
      echo "</SELECT>\n";
      echo "</FORM>\n";

      if($ph > $pw) {
        $height=intval($scaleimg/$thumbsz);
        $width=intval(($height/$ph)*$pw);
      } else {
        $width=intval($scaleimg/$thumbsz);
        $height=intval(($width/$pw)*$ph);
      }
      $pic->scaleimage($width*2,$height*2,true);
      $theImages=array();
      //$mysql->query("IF EXISTS unusedimgid DROP unusedimgid");
      $mysql->query("CREATE TEMPORARY TABLE unusedimgid SELECT imgid FROM thumblist");
      #for($y=0; $y<$height; $y++) 
      #  for($x=0; $x<$width; $x++) 
      #    $theImages[$x+$y*$width] = "";
      #for($remaining=$width*$height; $remaining>0; $remaining--) {
      #  $idx=0;
      #  for($offset=rand(0,$remaining-1); $offset>0; $offset--)
      #    {$idx++; while(strlen($theImages[$idx])>0) $idx++;}
      #  while(strlen($theImages[$idx])>0) $idx++;
      #  if(strlen($theImages[$idx])==0){
      #      $y=intval($idx/$width);
      #      $x=intval($idx-$y*$width);
      #      $colorSet=selectCollageSubImage($pic, $x, $y);
      #      insertCell($theImages, $idx, $colorSet);
      #  }
      #  else break;
      #}
      echo "<TABLE STYLE=\"font-size:0.25em;\" CELLPADDING='0' CELLSPACING='0'>\n";
      $plist=preg_split('/\//',$srcfname);
      echo "<TR><TH COLSPAN=" . $width . "><FORM ACTION='pix.php' METHOD='POST'><INPUT TITLE='" . $srcfname . "' TYPE='HIDDEN' NAME='SET' VALUE='" . $plist[4] . "'>";
      echo "<INPUT TYPE='IMAGE' NAME='IMG[" . $srcimgid . "]' SRC='thumbnail.php?IMGID=" . $srcimgid . "&SIZE=512'>";
      echo "</FORM></TH></TR>\n";
      for($y=0; $y<$height; $y++) {
        echo "<TR>\n";
        for($x=1; $x<$width; $x++) {
            $colorSet=selectCollageSubImage($pic, $x, $y); #
            insertCell($theImages, $x+$y*$width, $colorSet); #
            echo $theImages[$x+$y*$width];
        }
        echo "</TR>";
      }
      echo "</TABLE>";
?>
</BODY>
</HTML>
