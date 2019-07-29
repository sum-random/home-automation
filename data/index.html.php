<html>
<head>
<meta http-equiv='Refresh' content='300; url=/'>

<TITLE>Launch Pad</TITLE>
	<link type="text/css" href="/jscript/themes/base/ui.all.css" rel="stylesheet" />
  <script type="text/javascript" src="/jscript/jquery-1.3.2.js"></script>
  <script type="text/javascript" src="/jscript/ui/ui.core.js"></script>
  <script type="text/javascript" src="/jscript/ui/ui.slider.js"></script>
  <script type="text/javascript">
	$(function() {
		$("#SLVOL").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVvol: ui.value});
			}
		});
		$("#SLPCM").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVpcm: ui.value});
			}
		});
		$("#SLSPK").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVspeaker: ui.value});
			}
		});
		$("#SLLIN").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVline: ui.value});
			}
		});
		$("#SLMIC").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVmic: ui.value});
			}
		});
		$("#SLCD").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVcd: ui.value});
			}
		});
		$("#SLMIX").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVmix: ui.value});
			}
		});
		$("#SLREC").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVrec: ui.value});
			}
		});
		$("#SLIGN").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVigain: ui.value});
			}
		});
		$("#SLLN1").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVline1: ui.value});
			}
		});
		$("#SLMON").slider({
			min: 0,
			max: 100,
			step: 5,
			slide: function(event, ui) {
				$("#AMT").load("/cgi-bin/setmixer",{DEVmonitor: ui.value});
			}
		});
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=vol",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLVOL").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=pcm",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLPCM").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=speaker",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLSPK").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=line",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLLIN").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=mic",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLMIC").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=cd",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLCD").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=mix",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLMIX").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=rec",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLREC").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=igain",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLIGN").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=line1",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLLN1").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=monitor",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLMON").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=pcm",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLPCM").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=pcm",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLPCM").slider('value',amt);
	                        });
	    $("#AMT").load("/cgi-bin/getmixer",
	                      "DEV=pcm",
	                      function()
	                        {
	                        var amt=$("#AMT").text();
	                        $("#SLPCM").slider('value',amt);
	                        });
	    var ltlist = new Array("9","10","11","1","2","3","4","5","6","7","8","14");
	    for(ltnum in ltlist) {
	      getLampState(ltlist[ltnum]);
	    }
	});

function getLampState(lamp) {
  var la="#LRAUTO"+lamp;
  var ln="#LROn"+lamp;
  var lf="#LROff"+lamp;

  $("#AMT").load("/cgi-bin/getlight",
                 "DEV="+lamp,
                 function()
                 {
	               var amttxt=$("#AMT").text();
	               var amt=$("#AMT").text().split(":");
	               var rb="LR"+amt[1]+amt[0];
	               var td="#LC"+amt[0];
	               document.getElementById(rb).checked=true;
	               if(amt[1]=="AUTO") {
	                 $(td).css('background-color','#C0C0C0');
                   } else if(amt[1]=="Off") {
	                 $(td).css('background-color','#FFC0C0');
	               } else {
	                 $(td).css('background-color','#C0FFC0');
	               }
	             });

}

function setLampState(lamp, value) {
  $('#AMT').load('/cgi-bin/setlight?DEV'+lamp+'='+value,
                 {},
                 function() {setTimeout("getLampState("+lamp+")",1000)}
                 );
}

function changeSrcImg(id, img, descr)
  {
  $(id).html("<IMG ID='REPLIMG' SRC='" + img + "'><BR><CENTER>" + descr + "</CENTER>");
  $(id).css('position','absolute');
  $(id).css('top',$(window).height() / 2 - (($('#REPLIMG').height()/2)));
  $(id).css('left',$(window).width() / 2  - (($('#REPLIMG').width()/2)));
  $(id).css('visibility','visible');
  $(id).css('z-index','-1');
  $('#MIXER').hide();
  $('#LIGHTS').hide();
  $('#PLACES').hide();
  $('#WEATHER').hide();
  $('#DEVICES').hide();
  $('#MASTODON').hide();
  }

function changeSrcPage(id, page)
  {
  $('#MIXER').hide();
  $('#LIGHTS').hide();
  $('#PLACES').hide();
  $('#WEATHER').hide();
  $('#DEVICES').hide();
  $('#MASTODON').hide();
  $(id).css('visibility','visible');
  }

function changeSize(id, wd, ht)
  {
  $(id).css('width',wd);
  $(id).css('height',ht);
  }

function hideIt(id)
  {
  $(id).css('visibility','hidden');
  }

</script>
<style type="text/css">
div.pos_abs
{
position:absolute;
visibility:hidden;
}
div.navicons
{
}
img.bstyle
{
vertical-align:top;
width:48px;
height:32px;
border: 0px solid black;
cursor:pointer;
}
.social
{
width:80%;
display:none;
padding:15px;
background-image: url("/img/thematrix.gif");
width: 640;
height: 480;
color: white;
}
.circle
{
border-radius: 25px;
width: 50;
height: 50;
}
.whitelink
{
color: white;
}
.lights
{
width:80%;
display:none;
padding:5px;
padding-top:85px;
}
.devices
{
width:80%;
display:none;
padding:5px;
}
.weatherthumb
{
width:9%;
padding:1px;
border:1px solid black;
vertical-align:top;
}
.weathershow
{
width:80%;
padding:10px;
vertical-align:top;
border:none;
}
.weatherDiv
{
width:95%;
vertical-align:top;
padding:10px;
display:none;
}
.mixer
{
width:80%;
display:none;
padding-top:85px;
}
.track
{
width:80%;
text-align:center;
}
.loader
{
display:none;
}
td
{
border:1px solid black;
text-align:center;
padding-left:15px;
padding-right:15px;
}
</style>
</head>
<body>
<DIV CLASS='navicons' id='ICOBAR' >
<A HREF='http://www.claytontucker.com' onMouseOver='changeSrcImg("#myImage","/img/display_showcase.jpg", "Public website")' onMouseOut="hideIt('#myImage');" TARGET='_blank'>
<IMG CLASS='bstyle' ID='PUBICO' SRC='/img/display_showcase.jpg' onMouseOver='changeSize("#PUBICO",64,48);' onMouseOut='changeSize("#PUBICO",48,32);'></A>
<A HREF='/~*owner_name*/bookmarks.html' onMouseOver='changeSrcImg("#myImage","/img/bookmark1.jpg", "Bookmarks")' onMouseOut="hideIt('#myImage');" TARGET='_blank'>
<IMG CLASS='bstyle' ID='BKMICO' SRC='/img/bookmark1.jpg' onMouseOver='changeSize("#BKMICO",64,48);' onMouseOut='changeSize("#BKMICO",48,32);'></A>
<A HREF='/pix.php' onMouseOver='changeSrcImg("#myImage","/thumbnail.php?IMGID=84077&SIZE=FULL", "Family pix")' onMouseOut="hideIt('#myImage');" TARGET='_blank'>
<IMG CLASS='bstyle' ID='NATICO' SRC='/thumbnail.php?IMGID=84077&SIZE=64x48' onMouseOver='changeSize("#NATICO",64,48);' onMouseOut='changeSize("#NATICO",48,32);'></A>
<A onMouseOver="$('#LIGHTS').hide();$('#MIXER').hide();$('#WEATHER').hide();$('#MASTODON').hide();$('#DEVICES').hide();$('#PLACES').show();">
<IMG CLASS='bstyle' ID='SETICO' SRC='http://chart.apis.google.com/chart?cht=t&chs=440x220&chtm=usa&chf=bg,s,336699&chco=d0d0d0,cc0000&chd=s:99999999999999999999&chld=ALAZCACOHIKSMDNVNMOHOKTXUTWAWYORINKYILMI' onMouseOver='changeSize("#SETICO",64,48);' onMouseOut='changeSize("#SETICO",48,32);'></A>
<A HREF="https://mastodon.technology/web/accounts/149610" onMouseOver="$('#LIGHTS').hide();$('#MIXER').hide();$('#WEATHER').hide();$('#MASTODON').show();$('#DEVICES').hide();$('#PLACES').hide();">
<IMG CLASS='bstyle' ID='MSTICO' SRC='/img/antlion.jpg' onMouseOver='changeSize("#MSTICO",64,48);' onMouseOut='changeSize("#MSTICO",48,32);'></A>
<a href="http://www.facebook.com/people/Clayton-Tucker/100000813915752" title="Facebook" target="_blank"  onMouseOver="changeSrcImg('#myImage','http://badge.facebook.com/badge/100000813915752.224.1813268417.png', 'Facebook')" onMouseOut="hideIt('#myImage');" >
<img CLASS='bstyle' src="http://badge.facebook.com/badge/100000813915752.224.1813268417.png" width="48" height="32" style="border: 0px;" ID='FBLINK' onMouseOver='changeSize("#FBLINK",64,48);' onMouseOut='changeSize("#FBLINK",48,32);' /></a>
<A onMouseOver="$('#LIGHTS').hide();$('#PLACES').hide();$('#MIXER').hide();$('#MASTODON').hide();$('#DEVICES').hide();$('#WEATHER').show();">
<IMG CLASS='bstyle' ID='WTHICO' SRC='http://icons.wunderground.com/data/nids/MUX19_0.gif' onMouseOver='changeSize("#WTHICO",64,48);' onMouseOut='changeSize("#WTHICO",48,32);'></A>
<A HREF='/cgi-bin/lightsched' onMouseOver="changeSrcImg('#myImage','/img/AlarmClk.gif', 'Light scheduler')" onMouseOut="hideIt('#myImage');" TARGET='_blank'>
<IMG CLASS='bstyle' ID='SCHICO' SRC='/img/AlarmClk.gif' onMouseOver='changeSize("#SCHICO",64,48);' onMouseOut='changeSize("#SCHICO",48,32);'></A>
<A onMouseOver="$('#MIXER').hide();$('#PLACES').hide();$('#WEATHER').hide();$('#MASTODON').hide();$('#DEVICES').hide();$('#LIGHTS').show();">
<IMG CLASS='bstyle' ID='LITICO' SRC='/img/Light_Bulb.png' onMouseOver='changeSize("#LITICO",64,48);' onMouseOut='changeSize("#LITICO",48,32);'></A>
<A HREF='/music.php' onMouseOver="changeSrcImg('#myImage','/img/MusicNote.gif', 'Play music')" onMouseOut="hideIt('#myImage');" TARGET='_blank'>
<IMG CLASS='bstyle' ID='MUSICO' SRC='/img/MusicNote.gif' onMouseOver='changeSize("#MUSICO",64,48);' onMouseOut='changeSize("#MUSICO",48,32);'></A>
<A onMouseOver="$('#LIGHTS').hide();$('#PLACES').hide();$('#WEATHER').hide();$('#MASTODON').hide();$('#DEVICES').hide();$('#MIXER').show();">
<IMG CLASS='bstyle' ID='MIXICO' SRC='/img/Mixer.gif' onMouseOver='changeSize("#MIXICO",64,48);' onMouseOut='changeSize("#MIXICO",48,32);'></A>
<A onMouseOver="$('#DEVICES').load('/devices.php');$('#MASTODON').hide();$('#LIGHTS').hide();$('#PLACES').hide();$('#WEATHER').hide();$('#MIXER').hide();$('#DEVICES').show();">
<IMG CLASS='bstyle' ID='DEVICO' SRC='/img/google_vs_apple_thm.jpg' onMouseOver='changeSize("#DEVICO",64,48);' onMouseOut='changeSize("#DEVICO",48,32);'></A>
</DIV>

<DIV CLASS='mixer' ID='MIXER' >
<CENTER>
<DIV ID='SLVOL' CLASS='track'><FONT SIZE='1'>Volume</FONT></DIV><BR>
<DIV ID='SLPCM' CLASS='track'><FONT SIZE='1'>PCM</FONT></DIV><BR>
<DIV ID='SLSPK' CLASS='track'><FONT SIZE='1'>Speaker</FONT></DIV><BR>
<DIV ID='SLLIN' CLASS='track'><FONT SIZE='1'>Line</FONT></DIV><BR>
<DIV ID='SLMIC' CLASS='track'><FONT SIZE='1'>Mic</FONT></DIV><BR>
<DIV ID='SLCD' CLASS='track'><FONT SIZE='1'>CD</FONT></DIV><BR>
<DIV ID='SLMIX' CLASS='track'><FONT SIZE='1'>Mixer</FONT></DIV><BR>
<DIV ID='SLREC' CLASS='track'><FONT SIZE='1'>Record</FONT></DIV><BR>
<DIV ID='SLIGN' CLASS='track'><FONT SIZE='1'>IGain</FONT></DIV><BR>
<DIV ID='SLLN1' CLASS='track'><FONT SIZE='1'>Line 1</FONT></DIV><BR>
<DIV ID='SLMON' CLASS='track'><FONT SIZE='1'>Monitor</FONT></DIV><BR>
</CENTER>
</DIV>

<DIV CLASS='devices' ID='DEVICES'>
</DIV>

<DIV CLASS='social' ID='MASTODON' >
<A CLASS='whitelink' HREF="https://mastodon.technology/web/accounts/149610">
<IMG SRC='/img/antlion.jpg' CLASS='circle'><br>
@sum_random@Mastodon.Technology
</A>
</DIV>

<DIV CLASS='lights' ID='LIGHTS' >
<CENTER><FORM>
<TABLE><TR>
<script type="text/javascript">
  var llist=new Array("1:Computer","2:Sofa right","3:Shoes","4:Entryway","5:Television","6:Sofa left","10:Buffet Left","12:Buffet Right","14:Nathans computer");
  for(var lt in llist) {
    linf=llist[lt].split(":");
    document.write("<TD ID='LC" + linf[0] + "'><FONT SIZE='1'>"+linf[1]+"</FONT><BR>");
    document.write("<INPUT TYPE='RADIO' NAME='LG"+linf[0]+"' ID='LRAUTO"+linf[0]+"' onClick=\"setLampState("+linf[0]+",'AUTO');\">Auto");
    document.write("<INPUT TYPE='RADIO' NAME='LG"+linf[0]+"'  ID='LROff"+linf[0]+"' onClick=\"setLampState("+linf[0]+",'Off');\">Off");
    document.write("<INPUT TYPE='RADIO' NAME='LG"+linf[0]+"'   ID='LROn"+linf[0]+"' onClick=\"setLampState("+linf[0]+",'On');\">On");
    document.write("</TD>");
    if((lt) % 2 == 1)
      document.write("</TR><TR>");
  }
</SCRIPT>
</TR></TABLE>
</FORM>Light controls</CENTER>
</DIV>

<DIV CLASS='lights' ID='PLACES' >
<CENTER>
<p>Click on a place:</p>
<img src="http://chart.apis.google.com/chart?cht=t&chs=440x220&chtm=world&chf=bg,s,336699&chco=d0d0d0,cc0000&chd=s:99999&chld=USMXTHCHIT" width="440" height="220" usemap="#worldmap" />
<img src="http://chart.apis.google.com/chart?cht=t&chs=440x220&chtm=usa&chf=bg,s,336699&chco=d0d0d0,cc0000&chd=s:9999999&chld=AZCACOHINVNMTXWY" width="440" height="220" usemap="#usmap" />
<map name="worldmap">
  <area shape="poly" coords="342,96,349,104,344,118,338,100" alt="Thailand" href="/pix.php?SET=Vacation" TARGET='_blank' />
  <area shape="poly" coords="228,55,233,53,232,50,229,52" alt="Switzerland" href="/pix.php?SET=sets/CH" TARGET='_blank' />
  <area shape="poly" coords="77,76,84,91,107,101,112,94,103,97,100,86" alt="Mexico" href="/pix.php?SET=sets/MX" TARGET='_blank' />
  <area shape="poly" coords="228,56,237,56,241,62,238,68,230,57" alt="Italy" href="/pix.php?SET=sets/IT" TARGET='_blank' />
  <!--area shape="poly" coords="227,54,233,52,229,50,222,47,217,51,219,59,225,61,227,58" alt="France" href="/pix.php?SET=sets/FR" TARGET='_blank' /-->
</map>
<!--form method="get">
<input type="image" src="http://chart.apis.google.com/chart?cht=t&chs=440x220&chtm=world&chf=bg,s,336699&chco=d0d0d0,cc0000&chd=s:999999&chld=USMXTHCHITFR" alt="Submit" width="440" height="220">
</form-->
<map name="usmap">
  <area shape="rect" coords="120,109,171,74" alt="Colorado" href="/cgi-bin/pix?PICSET=CO" TARGET='_blank' />
  <area shape="poly" coords="3,65,35,65,35,87,76,125,76,143,57,143,33,129,8,92" alt="California" href="/pix.php?SET=sets/CA" TARGET='_blank' />
  <area shape="poly" coords="166,115,166,148,139,148,162,179,172,171,208,203,209,188,236,171,233,138,188,126,187,115" alt="Texas" href="/pix.php?SET=sets/TX" TARGET='_blank' />
  <area shape="poly" coords="82,110,119,110,119,155,103,156,77,143,77,125" alt="Arizona" href="/pix.php?SET=sets/AZ" TARGET='_blank' />
  <area shape="poly" coords="120,110,165,110,165,147,123,154" alt="New Mexico" href="/pix.php?SET=sets/NM" TARGET='_blank' />
  <area shape="poly" coords="36,65,36,87,76,126,81,110,81,65" alt="Nevada" href="/pix.php?SET=sets/NV" TARGET='_blank' />
  <area shape="poly" coords="161,199,152,208,109,172,118,167,148,181" alt="Hawaii" href="/pix.php?SET=sets/HI" TARGET='_blank' />
</map>
</CENTER>
</DIV>

<SPAN ID='AMT' CLASS='loader'></SPAN>

<DIV CLASS='pos_abs' id="myImage">
Test Data
</DIV>

<DIV CLASS='weatherDiv' ID='WEATHER' >
<CENTER>
<script language="JavaScript">
<!--
$(function () {
        var allLinks = document.getElementsByClassName("weatherthumb");

        for (var i=0; i< allLinks.length; i++) {
                allLinks[i].onmouseover = showWImg;
        }
        //document.getElementById("WEATHER").onmouseout = hideWImg;

});

function showWImg(evt) {
        if (evt) {
                var url = evt.target.src;
        }
        else {
                evt = window.event;
                var url = evt.srcElement.src;
        }

        var prevWin = document.getElementById("WEATHERIMG");
        prevWin.innerHTML = "<CENTER><IMG BORDER='5' SRC='" + url + "' CLASS='weathershow'></CENTER>";
        prevWin.style.visibility = "visible";
}

function hideWImg(evt) {
        var prevWin = document.getElementById("WEATHERIMG");
        prevWin.style.visibility = "hidden";
}

function y2k(number) { return (number < 1000) ? number + 1900 : number; }
function lz(number) { if(number < 10) document.write("0"); return number; }

function printdatecode() {
	//var date = new Date();
	//var date = new Date(y2k(date.getYear()),date.getMonth(),date.getDate(),date.getHours(),date.getMinutes(),date.getSeconds(), 7*60*60*1000);
	//document.write(y2k(date.getYear()));
	//document.write(lz(date.getMonth() + 1));
	//document.write(lz(date.getDate()));
	//document.write(".");
	//document.writeln(lz(date.getHours()));
	document.write("LATEST");
}

function printraindatecode() {
	var date = new Date();
	var date = new Date(y2k(date.getYear()),date.getMonth(),date.getDate(),date.getHours(),date.getMinutes(),date.getSeconds(), 7*60*60*1000);
	document.write(y2k(date.getYear()));
	document.write(lz(date.getMonth() + 1));
	document.write(lz(date.getDate()));
	document.write(".");
	document.writeln(lz(date.getHours()));
	document.writeln(lz(date.getMinutes() -  (date.getMinutes() % 30)));
	//document.write("LATEST");
}

function vapor() {
	document.write("<A HREF=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/vapor/");
	printdatecode();
	document.write(".jpg\" target=\"displayWin\"><IMG SRC=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/vapor/");
	printdatecode();
	document.write(".jpg\" alt=\"Water vapor image\" HEIGHT=150 WIDTH=200></A>");
}
function visible() {
	document.write("<A HREF=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/monterey_bay/vis/");
	printdatecode();
	document.write(".jpg\" target=\"displayWin\"><IMG SRC=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/monterey_bay/vis/");
	printdatecode();
	document.write(".jpg\" alt=\"Visible\" HEIGHT=150 WIDTH=200></A>");
}
function rainrate() {
	document.write("<A HREF=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/ir_color/");
	printraindatecode();
	document.write(".goes11.ir.pacus.jpg\" target=\"displayWin\">");
	document.write("<IMG SRC=\"http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/ir_color/");
	printraindatecode();
	document.write(".goes11.ir.pacus.jpg\" alt=\"Rain Rate\" HEIGHT=150 WIDTH=200></A>");
}
//-->
</script>
<SPAN>
<a href="http://www.nrlmry.navy.mil/sat-bin/epac_westcoast.cgi" title="EPAC Vapor" target="siteWin">
<img CLASS='weatherthumb' src="http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/vapor/LATEST.jpg" alt="Water vapor image"></a>
</SPAN>
<SPAN>
<a href="http://www.nrlmry.navy.mil/sat-bin/display10.cgi?PHOT=yes&CURRENT=LATEST.jpg&NAV=rain&AREA=pacific/eastern/pacus/ir_color" title="EPAC ir_color" target="siteWin">
<img CLASS='weatherthumb' src="http://www.nrlmry.navy.mil/archdat/pacific/eastern/pacus/ir_color/LATEST.jpg" alt="Rain rate"></a> 
</SPAN>
<SPAN>
<a href="http://www.nrlmry.navy.mil/sat-bin/epac_westcoast.cgi" title="Monterey visible" target="siteWin">
<img CLASS='weatherthumb' src="http://www.nrlmry.navy.mil/archdat/pacific/eastern/monterey_bay/vis/LATEST.jpg" alt="Visible"></a>
</SPAN> 
<SPAN>
<a href="http://www.wunderground.com/" title="San Francisco radar" target="siteWin">
<img src="https://radblast.wunderground.com/cgi-bin/radar/WUNIDS_map?station=MUX&brand=wui&num=6&delay=15&type=N0R&frame=0&scale=1.000&noclutter=0&showstorms=0&mapx=400&mapy=240&centerx=400&centery=240&transx=0&transy=0&showlabels=1&severe=0&rainsnow=0&lightning=0&smooth=0&rand=24768313&lat=0&lon=0&label=you" class="weatherthumb" id="radarmap" alt="Current RADR San Francisco CA"></a>
</SPAN>
<SPAN>
<a href="http://www.wunderground.com/" title="SW radar" target="siteWin">
<img src="https://icons.wxug.com/data/weather-maps/radar/united-states/reno-nevada-region-current-radar-animation.gif" CLASS='weatherthumb' alt="Current SW Radar"></a>
</SPAN>
<SPAN>
<a href="http://www.wunderground.com/" title="US radar" target="siteWin">
<img CLASS='weatherthumb' src="http://icons-ak.wxug.com/data/640x480/2xus_sf_anim.gif" alt="AccuWeather forecast map"></a>
</SPAN>
<SPAN>
<a href="http://www.wunderground.com/" title="US temperature" target="siteWin">
<img CLASS='weatherthumb' src="http://icons-ak.wxug.com/data/640x480/2xus_st_anim.gif" alt="Southwest Temperature"></a>
</SPAN>
<SPAN>
<a href="http://wxmaps.org/pix/clim.html" title="Precipitation forecast" target="siteWin">
<img CLASS='weatherthumb' src="http://wxmaps.org/pix/prec1.png" alt="Precipitation forecast"></a>
</SPAN>
<SPAN>
<a href="http://tropic.ssec.wisc.edu/real-time/mimic-tpw/epac/main.html" title="MIMIC-TPW" target="siteWin">
<img CLASS='weatherthumb' src="http://tropic.ssec.wisc.edu/real-time/mimic-tpw/epac/anim/latest72hrs.gif" alt="MIMIC-TPW"></a>
</SPAN>
<DIV ID='WEATHERIMG'> </DIV>
</CENTER>
</DIV>

</body>
</html>
