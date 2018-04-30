
function switchDiv(nextDiv) {
    [ '#MIXER', '#LIGHTS', '#PLACES', '#WEATHER', '#DEVICES' ].forEach(function(d) {
        d3.select(d)
          .style('display', 'none')
          .style('visibility', 'hidden');
    });
    if(nextDiv) {
        d3.select(nextDiv)
          .style('visibility', 'visible')
          .style('display', 'block');
    }
}

function lightColors(idx) {
  return { 'On':  [0,255,0],
           'Off': [255,0,0],
           'Auto': [128, 128, 128]}[idx];
}

function d3lights() {
    margin = {top: 10, bottom: 10, left: 20, right: 20};
    ldwidth = 600;
    lcols = 3;
    lcspacing = 15;
    lcwidth = (ldwidth - (lcspacing * lcols)) / lcols;
    lcheight = 70;
    d3.csv('/wsgi-bin/listlight', function(error, data) {
        if(error) throw error;
        lightsvg = d3.select('#LIGHTS')
            .append('svg')
                .attr('width', ldwidth + (lcspacing * lcols) + margin.left + margin.right)
                .attr('height', (lcheight + lcspacing) * parseInt(data.length / lcols + 0.5) + margin.top + margin.bottom)
                .append('g')
                     .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');
        data.forEach(function(d,i) {
            col = i % lcols
            row = parseInt(i / lcols)
            thislight = lightsvg.append('g')
                .attr('transform', 'translate(' + col * (lcwidth + lcspacing) + ', ' + row * (lcheight + lcspacing) + ')');
            lcbg = thislight.append('rect')
                .attr('x', 1)
                .attr('y', 1)
                .attr('width', lcwidth)
                .attr('height', lcheight)
                .attr('rx', lcwidth / 10)
                .attr('ry', lcheight / 10)
                .attr('border', '1px, black')
                .attr('fill', '#C0C0C0');
            thislight.append('text')
                .attr('x', lcwidth / 2)
                .attr('y', lcheight / 4)
                .attr('text-anchor', 'middle')
                .attr('fill', 'black')
                .attr('id', d.name)
                .text(d.name);
            ['On', 'Off', 'Auto'].forEach(function(state, idx) {
                thislight.append('text')
                    .attr('y', lcheight / 2 + (lcheight / 4.5))
                    .attr('x', (lcwidth / 24) + idx * (lcwidth / 3) + (lcwidth / 8))
                    .attr('text-anchor', 'middle')
                    .attr('fill', 'black')
                    .text(state);
                if(d.status == state) {
                    lc = lightColors(state);
                    thecolor = d3.rgb(lc[0], lc[1], lc[2], 0.5);
                } else {
                    thecolor = d3.rgb(128, 128, 128, 0.25);
                }
                clickrect = thislight.append('rect')
                    .attr('y', lcheight / 2)
                    .attr('x', (lcwidth / 24) + idx * (lcwidth / 3))
                    .attr('ry', 4)
                    .attr('rx', 4)
                    .attr('id', 'click' + d.name.replace(/ /g, ''))
                    .attr('width', lcwidth / 4)
                    .attr('height', lcheight / 3)
                    .attr('class', d.idx + ':' + state)
                    .on('mousedown', setlight)
                    .style('fill', thecolor);
            });
        });
    });
    function setlight() {
        console.log(this.classlist);
        therect = d3.select(this);
        thedata = this.classList.item(0).split(':');
        theidx = thedata[0];
        thestate = thedata[1];
        lc = lightColors(thestate);
        d3.selectAll('#' + this.id)
          .style('fill', d3.rgb(128, 128, 128, 0.25));
        d3.select(this)
          .style('fill', d3.rgb(lc[0], lc[1], lc[2], 0.5));
        console.log(theidx + '/' + thestate);
        d3.text('/wsgi-bin/setlight')
          .post('DEV=' + theidx + '\nSTATE=' + thestate, function(d) {  console.log(d);});
         
    }
}

function d3mixer() {
    margin = {top: 10, bottom: 10, left: 20, right: 20};
    console.log(d3.select('#ICOBAR'));
    slwidth = 600;
    slheight = 35; 
    thumbwidth = 15;
    slspacing = 9;
    thumbheight = slheight + 2;
    xpos = d3.scaleLinear().range([0, slwidth - thumbwidth]).domain([0,100]);
    mixstep = 1;
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

function changeSrcImg(id, img, descr) {
  switchDiv(id);
  var thebody = d3.select("body").node().getBoundingClientRect();
  d3.select(id)
    .html("<IMG ID='REPLIMG' SRC='" + img + "'><BR><CENTER>" + descr + "</CENTER>");
  var theimg = d3.select("#REPLIMG").node().getBoundingClientRect();
  d3.select(id)
    .style('position','absolute')
    .style('top',thebody.height / 2 - ((theimg.height/2)))
    .style('left',thebody.width / 2  - ((theimg.width/2)))
    .style('visibility','visible')
    .style('display','block')
    .style('z-index','-1');
}

function changeSrcPage(id, page) {
  switchDiv(id);
  d3.select(id)
    .style('display','block')
    .style('visibility','visible');
}

function changeSize(id, wd, ht) {
  d3.select(id)
    .style('width',wd)
    .style('height',ht);
}

function hideIt(id) {
  d3.select(id)
    .style('display','none')
    .style('visibility','hidden');
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
