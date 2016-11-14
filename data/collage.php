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
//include("inc/pdo.php");
//include("inc/functions.php");
include("generatethumbs.php");

global $mysql,$base,$log;

if(array_key_exists('IMGID',$_REQUEST)) {
  foreach($mysql->query("SELECT fname,imgid FROM thumblist WHERE imgid=" . $_REQUEST['IMGID']) as $row) 
    if(file_exists($row[0])) {
      $fname=$row[0];
      $imgid=$row[1];
    }
} else if(array_key_exists('IMGMATCH',$_REQUEST)) {
  $row=matchImage($_REQUEST['IMGMATCH']);
    if(file_exists($row[0])) { 
      $fname=$row[0];
      $imgid=$row[1];
    }
} else {
  echo "Missing IMG";
  exit(1);
}

      $pic=new Imagick();
      $pic->clear();
      $pic->readImage($fname);
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
      echo "<TABLE STYLE=\"font-size:0.25em;\" CELLPADDING='0' CELLSPACING='0'>\n";
      $plist=preg_split('/\//',$fname);
      echo "<TR><TH COLSPAN=" . $width . "><FORM ACTION='pix.php' METHOD='POST'><INPUT TITLE='" . $fname . "' TYPE='HIDDEN' NAME='SET' VALUE='" . $plist[4] . "'>";
      echo "<INPUT TYPE='IMAGE' NAME='IMG[" . $imgid . "]' SRC='thumbnail.php?IMGID=" . $imgid . "&SIZE=512'>";
      echo "</FORM></TH></TR>\n";
      for($y=0; $y<$height; $y++) {
        echo "<TR>\n";
        $nxtRow=array();
        for($x=1; $x<$width; $x++) {
            $impul=$pic->getImagePixelColor($x*2,$y*2);
            $colorsul=$impul->getColor();
            $impur=$pic->getImagePixelColor($x*2-1,$y*2);
            $colorsur=$impur->getColor();
            $impll=$pic->getImagePixelColor($x*2,$y*2+1);
            $colorsll=$impll->getColor();
            $implr=$pic->getImagePixelColor($x*2-1,$y*2+1);
            $colorslr=$implr->getColor();
            $imgquery=$colorsul['r'] . ":" . $colorsul['g'] . ":" . $colorsul['b'] . ":" . $colorsur['r'] . ":" . $colorsur['g'] . ":" . $colorsur['b'] . ":" . $colorsll['r'] . ":" . $colorsll['g'] . ":" . $colorsll['b'] . ":" . $colorslr['r'] . ":" . $colorslr['g'] . ":" . $colorslr['b'];
            $imgsrc="thumbnail.php?COLLAGEQUERY=" . $imgquery;
            $bgcolor=sprintf("%02X%02X%02X",($colorsul['r']+$colorsur['r']+$colorsll['r']+$colorslr['r'])/4,($colorsul['g']+$colorsur['g']+$colorsll['g']+$colorslr['g'])/4,($colorsul['b']+$colorsur['b']+$colorsll['b']+$colorslr['b'])/4);
            $nxtRow[$x]="<TD STYLE='background-color: #" . $bgcolor . ";' bgcolor='" . $bgcolor . "'><A TITLE='" . $bgcolor . "' HREF='/collage.php?IMGMATCH=" . $imgquery . "&THUMBSZ=" . $thumbsz . "&SCALE=" . $scaleimg . "' BORDER='0' ><IMG ID='IMGCELL' onMouseOver='showPreview();' onMouseOut='hidePreview();' BORDER='0' ALT='" . $imgquery . "' SRC='" . $imgsrc . "&SIZE=" . $thumbsz . "x" . $thumbsz . "' HEIGHT='" . $thumbsz . "' WIDTH='" . $thumbsz . "'></A></TD>\n";
        }
        foreach($nxtRow as $cells)
          echo $cells;
        echo "</TR>";
      }
      echo "</TABLE>";
?>
</BODY>
</HTML>
