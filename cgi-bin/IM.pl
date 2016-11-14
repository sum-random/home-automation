#!/usr/local/bin/perl

use strict;

use Image::Magick;
use IO::Handle;

`renice 20 $$ 2>&1 >/dev/null`;
$| =1;

my($maxdim, $elementsz, $screensz, @oa, @thisrow, @lastrow, $ol, $op, $ok, $ov, $image, $x, $xp, $yp, $wd, $ht, $cc, $pl, $rd, $bl, $gr, $dst, $sdst, $color, $fname, $base, $title, $colorline, @pixel, $pixval, $clrval, $sfn, $checkit);
my ($rw, $gw, $bw);

my %opts=();
if (length ($ENV{'QUERY_STRING'}) > 0){
  $ol=$ENV{'QUERY_STRING'};
  @oa=split(/&/,$ol);
  foreach $op (@oa) {
    ($ok, $ov)=split(/=/,$op);
    $ov =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
    $opts{$ok}=$ov;
  }
}

$base="/storage/Image";

$fname=$opts{'IMG'};
if($fname eq "") { $fname='/img/nathan0/thumbsize/IMG_00000.JPG'; }
$elementsz=$opts{'ESZ'};
if($elementsz eq "") { $elementsz=32; }
$screensz=$opts{'SSZ'};
if($screensz eq "") { $screensz=640; }
$maxdim=int($screensz / $elementsz);
$image = Image::Magick->new;
$x = $image->Read("$base/" . substr($fname,5));
warn "$x" if "$x";

$title="$fname";

print "Content-type: text/html; charset=iso-8859-1\n\n";
print "<HTML><HEAD><TITLE>$title</TITLE>\n";
print "<script type=\"text/javascript\" src=\"/jscript/IM.js\"></script>\n";
print "</HEAD>";
print "<BODY>\n";
print "<TABLE><TR><TD>\n";
print "<IMG SRC='$fname'><BR>\n";
print "</TD><TD ALIGN='LEFT'>\n";
print "Element size: ";
for($x=4 ; $x <= 32 ; $x += 2) {
  print "<A HREF='?IMG=$fname&ESZ=$x&SSZ=$screensz'>$x</A> ";
}
print "<BR>\n";
print "Screen size: ";
print "<A HREF='?IMG=$fname&ESZ=$elementsz&SSZ=640'>640</A> ";
print "<A HREF='?IMG=$fname&ESZ=$elementsz&SSZ=800'>800</A> ";
print "<A HREF='?IMG=$fname&ESZ=$elementsz&SSZ=1024'>1024</A> ";
print "<A HREF='?IMG=$fname&ESZ=$elementsz&SSZ=1280'>1280</A> ";
print "<A HREF='?IMG=$fname&ESZ=$elementsz&SSZ=1920'>1920</A> ";
print "</TD></TR></TABLE>\n";

my %clist = ();
open FH, "../cgi-data/thumblist.txt" or die $!;
while($colorline=<FH>) {
  chomp $colorline;
  ($color, $fname) = split(/ /,$colorline);
  chomp $color; chomp $fname;
  $clist{"$color"}="$fname";
}
close FH;


$ht=$image->Get('height');
$wd=$image->Get('width');
if($ht > $maxdim || $wd > $maxdim) {
  if($ht > $wd) {
    $wd=int($wd * ($maxdim / $ht));
    $ht=$maxdim;
  } else {
    $ht=int($ht * ($maxdim / $wd));
    $wd=$maxdim;
  }
  $image->Resize(width=>$wd,height=>$ht,filter=>'Cubic');
}

print "<DIV ID='POPWIN' STYLE='position:absolute;'> </DIV>\n";
my @array=keys(%clist);
my $size=$#array;
if($size/4<$wd*$ht) { $size=0; }

my %usedlist=();
print "<TABLE STYLE=\"font-size:0.25em;\" CELLSPACING='0' CELLPADDING='0' >\n";
  
for($yp=0;$yp<$ht;$yp++) {
  print "<TR>\n";
  for($xp=0;$xp<$wd;$xp++) {
      $cc = "";
      @pixel = $image->GetPixel(map=>'RGB', x=>$xp, y=>$yp, normalize=>'true');
      if($pixel[0] > $pixel[1] && $pixel[0] > $pixel[2]) {
        $rw = 4;
        if($pixel[1] > $pixel[2]) {
          $gw=3; $bw=2;
        } else {
          $gw=2; $bw=3;
        }
      } elsif($pixel[1] > $pixel[0] && $pixel[1] > $pixel[2]) {
        $gw=4;
        if($pixel[0] > $pixel[2]) {
          $rw=3; $bw=2;
        } else {
          $bw=3; $rw=2;
        }
      } else {
        $bw=4;
        if($pixel[0] > $pixel[1]) {
          $rw=3; $gw=2;
        } else {
          $gw=3; $rw=2;
        }
      }
        
      foreach $pixval (@pixel) { $cc = $cc . sprintf "%02X", $pixval * 255; }
      print "<TD STYLE='background-color:$cc'>";
      $pl="";
      $sdst=1048576;
      $sfn="";
      while(($clrval, $fname)=each(%clist)) { 
        $checkit='true';
        if($size > 0) { if($usedlist{$fname} eq 'true') {$checkit='false';}}
        if($checkit eq 'true') {
          $rd=abs($pixel[0]*255 - hex(substr($clrval,0,2)));
          $gr=abs($pixel[1]*255 - hex(substr($clrval,2,2)));
          $bl=abs($pixel[2]*255 - hex(substr($clrval,4,2)));
          $dst=int($rd + $gr + $bl);
          if(($dst < $sdst)) { $pl = $clrval; $sdst=$dst; $sfn=$fname; } 
        }
      }
      $usedlist{$sfn} = "true";
      my $wfn=$sfn;
      $wfn=~s/thumbsize/websize/;
      print "<A HREF='?IMG=$wfn&ESZ=$elementsz&SSZ=$screensz' TITLE='$cc $pl $sdst'>";
      print "<IMG WIDTH='$elementsz' ID='IMGCELL' HEIGHT='$elementsz' BORDER='0' SRC='$sfn'>";
      print "</A></TD>\n";
      STDOUT->flush();
  }
  print "</TR>";
}

print "</TABLE>\n";
print "</BODY></HTML>\n";

