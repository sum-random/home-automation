<!DOCTYPE HTML>
<HTML><HEAD><TITLE>Manage duplicate files</TITLE>
<?php
include("inc/pdo.php");
include("inc/functions.php");

global $mysql,$base,$log;
$base="/usr/local/media/";
$cksumcolors=array("#FF8080","#80FF80","#8080FF");
$inodecolors=array("#FFC080","#C0FF80","#C080FF","#FF80C0","#80FFC0","#80C0FF");
$ckcolor=0;$icolor=0;

if(array_key_exists('MANUEL',$_REQUEST)) {
  // Perform reuested actions
  $onames=$_REQUEST['ORIGINALFNAME'];
  foreach($_REQUEST['FNAME'] as $fileid=>$fname) {
    if($fname !== $onames[$fileid]) {
      $parentinfo=sqlquery("SELECT filename FROM musicfiles WHERE fileid=" . $fileid);
      $fpath=dirname(urldecode($parentinfo[0][0]));
      $parent=basename($fpath);
      write_log($base . $fpath . '/' . $onames[$fileid].$base . $fpath . '/' . $fname);
      write_log("UPDATE musicfiles SET filename='" . urlencode($fpath . '/' . $fname) . "',shortname='" . $parent . " - " . $fname . "' WHERE fileid=" . $fileid);
    }
  }
  if(array_key_exists('INODEACTION',$_REQUEST)) {
    foreach($_REQUEST['INODEACTION'] as $fileid=>$act) {
      $fileinfo=sqlquery("SELECT filename FROM musicfiles WHERE fileid=" . $fileid);
      if($act == "DELETE")
        write_log("DELETE " . $fileinfo[0][0]);
      else {
        $fileact=preg_split('/:/',$act);
        if($fileact[0] == 'JOIN') {
          $parentinfo=sqlquery("SELECT filename FROM musicfiles WHERE fileid=" . $fileact[1]);
          $fpath=dirname(urldecode($parentinfo[0][0]));
          write_log("hardlink " . $parentinfo[0][0] . " to " . $fileinfo[0][0]);
        }
      }
    }
  }
}

?>
</HEAD>
<BODY>
<FONT SIZE='1'>
<FORM METHOD='POST'>
<TABLE>
<TR><TD>Number of checksums per page: </TD>
<TD><SELECT NAME='PERPAGE' onChange='submit();'>
<?php
$perpage=20;
if(array_key_exists('PERPAGE',$_REQUEST))
  $perpage=$_REQUEST['PERPAGE'];
foreach(array(5,10,20,50,100) as $num) {
  echo "<OPTION VALUE=" . $num . ($perpage == $num ? " SELECTED" : "") . ">" . $num . "</OPTION>\n";
}
?>
</SELECT></TD></TR>
<TR><TD>Starting page: </TD>
<TD><SELECT NAME='WHICHPAGE' onChange='submit();'>
<?php
$whichpage=0;
if(array_key_exists('WHICHPAGE',$_REQUEST))
  $whichpage=$_REQUEST['WHICHPAGE'];
$query="select count(*) from (select checksum,count(*) from musicfiles where checksum is not null group by checksum having count(*)>1) a";
foreach($mysql->query($query) as $row) {
    $maxpage=intval($row[0] / $perpage);
    if($row[0] % $perpage > 0)
      $maxpage++;
    if($whichpage > $maxpage)
      $whichpage=$maxpage-1;
    echo "<!-- maxpage " . $maxpage . " whichpage " . $whichpage . "-->\n";
    for($pnum=0;$pnum<$maxpage;$pnum++)
      echo "<OPTION VALUE=" . $pnum . ($whichpage == $pnum ? " SELECTED" : "") . ">" . ($pnum + 1) . "</OPTION>\n";
}
?>
</SELECT></TD></TR></TABLE>
<TABLE><TR><TH>Checksum</TH><TH>Inode</TH><TH>File</TH><TH>Join</TH><TH>Delete</TH></TR>
<?php
$query="select checksum,count(*) from musicfiles where checksum is not null group by checksum having count(*)>1 limit " . $perpage . " offset " . $perpage * $whichpage;
foreach($mysql->query($query) as $ckrow) {
    $ckcolor++;
    if($ckcolor>=count($cksumcolors)) $ckcolor=0;
    unset($masternode);
    $inodeqry="SELECT inode, count(*) FROM musicfiles WHERE checksum='" . $ckrow[0] . "' group by inode order by 2 desc, 1";
    foreach($mysql->query($inodeqry) as $inoderow) {
        $icolor++;
        if($icolor>=count($inodecolors))
          $icolor=0;
        if(!isset($masternode)) {
          $masternode=$inoderow[0];
          $masternodecolor=$inodecolors[$icolor];
        }
        $filequery="SELECT DISTINCT filename, fileid FROM musicfiles WHERE inode=" . $inoderow[0];
        foreach($mysql->query($filequery) as $filerow) {
            $canaction=$inoderow[1]==1 && $inoderow[0] != $masternode;
            $decodefile=urldecode($filerow[0]);
            $fname=str_replace("'","&#39;",basename($decodefile));
            $fpath=dirname($decodefile);
            echo "<TR BGCOLOR='" . $cksumcolors[$ckcolor] . "'><TD>" . $ckrow[0] . "</TD><TD BGCOLOR='" . $inodecolors[$icolor] . "'>" . $inoderow[0] . "</TD><TD>" . $fpath . "/<INPUT NAME='ORIGINALFNAME[" . $filerow[1] . "]' TYPE='HIDDEN' VALUE='" . $fname . "'><INPUT NAME='FNAME[" . $filerow[1] . "]' TYPE='TEXT' SIZE='" . strlen($fname) . "' VALUE='" . $fname . "'></TD><TD" . ($canaction ? " BGCOLOR='" . $masternodecolor . "'>Link file to inode " . $masternode . "<INPUT TYPE='RADIO' NAME='INODEACTION[" . $filerow[1] . "]' VALUE='JOIN:" . $filerow[1] . ":" . $masternode . "'>" : ">") . "</TD><TD>Delete <INPUT TYPE='" . ($canaction ? "RADIO" : "CHECKBOX" ) . "' NAME='INODEACTION[" . $filerow[1] . "]' VALUE='DELETE'></TD></TR>\n";
        }
    }
} 
        

?>
</TABLE>
<INPUT TYPE='SUBMIT' NAME='MANUEL' VALUE='Go'>
</FORM>
<PRE>
<?php
print_r($_REQUEST);
?>
</PRE>
</FONT>
</BODY></HTML>
