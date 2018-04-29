	$(function() {
	    var ltlist = new Array("9","10","11","1","2","3","4","5","6","8","14");
	    for(ltnum in ltlist) {
	      getLampState(ltlist[ltnum]);
	    }
	});


function hideDivs() {
    $('#LIGHTS').hide();
    $('#PLACES').hide();
    $('#WEATHER').hide();
    $('#DEVICES').hide();
    $('#MIXER').hide()
}


function d3mixer() {
    margin = {top: 10, bottom: 10, left: 20, right: 20};
    slwidth = 600;
    slheight = 35; 
    thumbwidth = 15;
    slspacing = 9;
    thumbheight = slheight + 2;
    xpos = d3.scaleLinear().range([0, slwidth - thumbwidth]).domain([0,100]);
    mixstep = 3;
    mixpos = d3.scaleLinear().range([1, 100]).domain([thumbwidth, slwidth - thumbwidth]);
    

    d3.csv('/wsgi-bin/listmixer', function(error, data) {
      if(error) throw error;
      mixsvg = d3.select('#MIXER')
                 .append('svg')
                   .attr('width', slwidth + margin.left + margin.right)
                   .attr('height', slheight * data.length + slspacing * (data.length - 1) + margin.top + margin.bottom)
                   .append('g')
                     .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');
      // process data
      data.forEach(function(d,i) {
        d.left = +d.left;
        d.right = +d.right;
        slider = mixsvg.append('g')
            .attr('transform', 'translate(0, ' + (slheight + slspacing) * i + ')');
        slider.append('rect')
            .attr('x', 1)
            .attr('y', 0)
            .attr('rx', slheight / 3)
            .attr('ry', slheight / 3)
            .attr('width', slwidth)
            .attr('height', slheight)
            .style('fill', '#C0C0C0');
        slider.append('text')
            .attr('x', slwidth / 2)
            .attr('y', slheight / 2)
            .attr('enabled', false)
            .attr('fill', 'black')
            .attr('text-anchor', 'middle')
            .text(d.device);
        slider.append('rect')
            .style('fill', d3.rgb(255,0,0,0.50))
            .attr('y', -1)
            .attr('x', xpos((d.left+d.right)/2))
            .attr('rx', thumbwidth / 3)
            .attr('ry', thumbheight / 3)
            .attr('height', thumbheight)
            .attr('width', thumbwidth)
            .attr('enabled', false)
            .attr('id', 'thumb' + d.device);
        slider.append('rect')
            .attr('x', 0)
            .attr('y', -1)
            .attr('width', slwidth)
            .attr('height', thumbheight)
            .attr('id', d.device)
            .on('mousedown', startDrag)
            .on('mousemove', dragIt)
            .on('mouseup', endDrag)
            .on('mouseout', endDrag)
            .style('fill', d3.rgb(0,0,0,0));
        function startDrag() {
            this.candrag = true;
            this.vp = mixstep * parseInt(mixpos(d3.mouse(this)[0])/mixstep);
            thethumb = d3.select('#thumb' + this.id);
            thethumb.candrag = true;
            thethumb.attr('style', 'fill: rgba(255,0,0,1);');
            thethumb.attr("x", d3.mouse(this)[0] - thumbwidth / 2);
        }
        function endDrag() {
            thethumb = d3.select('#thumb' + this.id);
            this.candrag = false;
            thethumb.candrag = false;
            thethumb.attr('style', 'fill: rgba(255,0,0,0.50);');
        }
        function dragIt() {
            thethumb = d3.select('#thumb' + this.id);
            if(this.candrag || thethumb.candrag){
                var mx = d3.mouse(this)[0];
                var vp = parseInt(mixpos(mx)/mixstep)*mixstep;
                vp = (vp>100?100:vp<0?0:vp);
                var tp = xpos(vp);
                thethumb.attr("x", tp);
                if(this.vp != vp) {
                    this.vp = vp;
                    d3.text('/wsgi-bin/setmixer')
                      .post('DEV=' + this.id + '\nVALUE=' + vp, function(d) {  console.log(d);});
                }
            }
        }
      });
    });
}

function getLampState(lamp) {
  var la="#LRAUTO"+lamp;
  var ln="#LROn"+lamp;
  var lf="#LROff"+lamp;

  $("#AMT").load("/wsgi-bin/getlight",
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
  hideDivs();
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
  }

function changeSrcPage(id, page)
  {
  hideDivs();
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
