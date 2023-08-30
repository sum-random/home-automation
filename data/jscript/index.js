function setupWeather() {
  d3.selectAll('.weatherthumb')
    .on('mouseover', showWImg);
}

function showOneLightSchedule() {
    thelight = d3.select("#PICKALIGHT").node().value;
    the_display = d3.select("#LIGHTSCHED").select("#SCHEDLIST");
    if(thelight > -1) {
        d3.tsv('/getonelightsched/' + thelight, function(rawdata) {
            data = rawdata.sort(function(d){return d.descr;})
            the_options = the_display.selectAll("option").data(data, function(d){return d.id;});
            the_options.exit().remove();
            the_options.enter().append("option");
            the_display.selectAll("option")
                .attr('value', function(d) {return d.id;})
                .text(function(d){return d.descr;});
            the_display.attr("size", data.length<2?2:data.length);
            showScheduleItem();
        });
        d3.select('#DIVSCHED').style('visibility','visible');
    } else {
        the_display.selectAll("option").remove();
        the_display.attr("size", 4);
        d3.select('#UPDATE').style('visibility','hidden');
        d3.select('#DELETE').style('visibility','hidden');
        d3.select('#DIVSCHED').style('visibility','hidden');
    }
}

function showScheduleItem() {
    the_item = d3.select("#SCHEDLIST").node().value;
    if(the_item.length > 0)
        d3.json('/getlightscheddetail/' + the_item, function(data) {
            d3.select('#MONTHMATCH').node().value = data['monthmatch'];
            d3.select('#DAYMATCH').node().value = data['daymatch'];
            d3.select('#TURNON').node().value = data['turnon'];
            d3.select('#TURNOFF').node().value = data['turnoff'];
            d3.select('#UPDATE').style('visibility','visible');
            d3.select('#DELETE').style('visibility','visible');
            d3.select('#MAKENEW').style('visibility','hidden');
        });
    else {
        d3.select('#MONTHMATCH').node().value = '*';
        d3.select('#DAYMATCH').node().value = '*';
        d3.select('#TURNON').node().value = 'HHMM';
        d3.select('#TURNOFF').node().value = 'HHMM';
        d3.select('#UPDATE').style('visibility','hidden');
        d3.select('#MAKENEW').style('visibility','hidden');
        d3.select('#DELETE').style('visibility','hidden');
    }
}

function showNewButton() {
    if(
       d3.select('#TURNON').node().value * 1 > 0 &&
       d3.select('#TURNON').node().value.length == 4 &&
       d3.select('#TURNOFF').node().value * 1 > 0 &&
       d3.select('#TURNOFF').node().value.length == 4 &&
       true
)
        d3.select('#MAKENEW').style('visibility','visible');
    else
        d3.select('#MAKENEW').style('visibility','hidden');
}

function submitScheduleUpdate(newItem=false) {
    d3.json('/setlightscheddetail')
      .post('the_id='+d3.select('#SCHEDLIST').node().value+'\nthe_hhcode=I\nthe_lightcode='+d3.select('#PICKALIGHT').node().value+'\nthe_month='+d3.select('#MONTHMATCH').node().value+'\nthe_day='+d3.select('#DAYMATCH').node().value+'\nthe_on_time='+d3.select('#TURNON').node().value+'\nthe_off_time='+d3.select('#TURNOFF').node().value+'\nnew_item='+(newItem?'true':'false')+'\n', function(data) {
        showOneLightSchedule();
        showScheduleItem();
       });
}

function deleteScheduleItem() {
    d3.json('/deletelightscheddetail')
        .post('the_id='+d3.select('#SCHEDLIST').node().value, function(data) {
            showOneLightSchedule();
            //showScheduleItem();
       });

}

function populateMusicList() {
    thetextfield = document.getElementById("TUNEFILTER");
    thetext = thetextfield.value;
    thelistdisplay = d3.select("#MUSICDIV").select("#TUNELIST");
    if(thetext.length > 3) {
        d3.csv('/getmusic?filter=' + thetext, function(rawdata) {
            data = rawdata.sort(function(d){return d.shortname;})
            theoptions = thelistdisplay.selectAll("option").data(data, function(d){return d.shortname;});
            theoptions.exit().remove();
            theoptions.enter().append("option");
            thelistdisplay.selectAll("option")
              .attr('value', function(d) {return d.fileid;})
              .text(function(d) {return d.shortname;});
            thelistdisplay.attr("size", data.length);
        });
    } else {
        thelistdisplay.selectAll("option").remove();
        thelistdisplay.attr("size", 4);
    }
}

function addtunes() {
    d3.select("#MUSICDIV").select("#TUNELIST").selectAll("option")
        .filter(function(d,i) { return this.selected;})
        .selectAll(function(d, i) { 
            d3.text('/addplaylist', function() {})
                .post("fileid="+d.fileid);
        });
}

function rmtunes() {
    d3.select("#MUSICDIV").select("#TUNELIST").selectAll("option")
        .filter(function(d,i) { return this.selected;})
        .selectAll(function(d, i) { 
            d3.text('/rmplaylist', function() {})
                .post("fileid="+d.fileid);
        });
}

function d3weather() {
      thethumb = d3.select(this);
      thediv = d3.select('#WEATHERIMG');
      thediv.select('svg').remove();
      thediv.append('svg').append('svg:image')
        .attr('width', '90%')
        .attr('class', 'weatherShow')
        .attr('xlink:href', thethumb.attr('src'));
}

function switchDiv(nextDiv) {
    [ '#PIX', '#FULLSZ', '#MIXER', '#LIGHTS', '#PLACES', '#WEATHER', '#DEVICES', '#BOOKMARKS', '#MASTODON', '#MUSICDIV', '#LIGHTSCHED' ].forEach(function(d) {
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

function populateThumbs() {
    margin = {top: 10, bottom: 10, left: 20, right: 20};
    imgsz = { size: 48, spacing: 0 } ;
    breakpt = 200;
    
    fldr = d3.select("#PICKFOLDER").node().value;
    d3.select("#PIX").select('svg').remove();
    slider = d3.select("#PIX").append('svg')
        .attr('id','SLIDESVG')
        .attr('width', '100%')
        .on('mousemove', scrollThumbs);
    slider.append('rect')
        .attr('width',3)
        .attr('color','red;')
        .style('visibility', 'hidden')
        .style('opacity','0.5;')
        .attr('id','TRACKER');
    imgrect = slider.append('g')
        .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')')
        .attr('id','IMGSLIDER');
    d3.json("/getimages")
        .post("the_folder_id="+fldr, function(error, data) {
            if(error) throw error;
            slider.attr('height', Math.floor(data.length/breakpt + 1)*(imgsz.size + imgsz.spacing) + 'px');
            data.forEach(function(d,i) {
              imgrect.append('svg:image')
                .attr('x', (i % breakpt) * (imgsz.size + imgsz.spacing))
                .attr('y', Math.floor(i/breakpt) * (imgsz.size + imgsz.spacing))
                .attr('height', imgsz.size)
                .attr('href', "/thumbnail?IMGID="+d.imgid+"&SIZE="+imgsz.size)
                .attr('alt', d.fname)
                .on('mouseout', function(d,i) {
                    d3.select(this)
                      .attr("border", "0px,black");
                })
                .on('mouseenter', function(d2,i) {
                    d3.select(this)
                        .attr("border", "1px,green");
                    expandImage("/thumbnail?IMGID="+d.imgid);
                });
            });
        });
}

function expandImage(uri) {
    evt = window.event;
    console.log(uri);
    ht = window.innerHeight - 40;
    d3.select("#FULLSZ")
      .style('visibility', 'visible')
      .style('display', 'block')
      .select('svg').remove();
    display = d3.select("#FULLSZ").append('svg')
        .attr('width', '100%')
        //.attr('height', '100%')
        .attr('id', 'BIGIMGSVG')
        .append('g')
            .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')')
            //.attr('height', ht)
            .attr('href',uri+"&SIZE=" + ht);
    display.append('svg:image')
        .attr('x', 0)
        .attr('y', 0)
        .attr("xlink:href", uri+"&SIZE=" + ht)
        .attr('alt', evt.srcElement.href.baseVal)
        .attr('id','BIGIMG')
        .on('load', function(){
            var element = document.getElementById("BIGIMG");
            //console.log(pw);
            d3.select('#FULLSZ')
                .attr('height',element.getBoundingClientRect().height + "px");
            d3.select('#BIGIMGSVG')
                .attr('height',element.getBoundingClientRect().height + "px");
        });
    scrollThumbs();
}

function scrollThumbs() {
    var evt = window.event;
    var track = d3.select("#TRACKER");
    var panel = d3.select("#IMGSLIDER");
    var element = document.getElementById("IMGSLIDER");
    var pw = element.getBoundingClientRect().width;
    var wrapper = document.getElementById("SLIDESVG");
    var span = wrapper.getBoundingClientRect().width;
    var scale = d3.scaleLinear()
       .domain([10,span-10])
       .range([0,-(pw-span)]);
    if(window.innerWidth < pw) {
        var moveTo =  scale(evt.pageX);
        if(moveTo > 20)
            moveTo = 20;
        if(moveTo < -(pw-span))
            moveTo = -(pw-span); 
        track
            .style('visibility', 'visible')
            .attr('height',wrapper.getBoundingClientRect().height+'px')
            .attr('transform','translate(' + (evt.pageX - 9) + ',0)');
        panel
            .attr('transform', 'translate(' + moveTo + ',10)');
    }
    //console.log('pw:' + pw + ' pageX:' + evt.pageX + ' innerWidth:' + window.innerWidth + ' scale:' + scale(evt.pageX) + ' span:' + span);
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
    d3.csv('/listlight', function(error, data) {
        if(error) throw error;
        d3.select('#LIGHTS').selectAll('svg').remove();
        lightsvg = d3.select('#LIGHTS')
            .append('svg')
                .attr('width', ldwidth + (lcspacing * lcols) + margin.left + margin.right)
                .attr('height', (lcheight + lcspacing) * parseInt(data.length / lcols + lcols) + margin.top + margin.bottom)
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
        therect = d3.select(this);
        thedata = this.classList.item(0).split(':');
        theidx = thedata[0];
        thestate = thedata[1];
        lc = lightColors(thestate);
        d3.selectAll('#' + this.id)
          .style('fill', d3.rgb(128, 128, 128, 0.25));
        d3.select(this)
          .style('fill', d3.rgb(lc[0], lc[1], lc[2], 0.5));
        d3.text('/setlight')
          .post('DEV=' + theidx + '\nSTATE=' + thestate, function(d) {  console.log(d);});
         
    }
}

function d3mixer() {
    margin = {top: 10, bottom: 10, left: 20, right: 20};
    slwidth = 600;
    slheight = 35; 
    thumbwidth = 15;
    slspacing = 9;
    thumbheight = slheight + 2;
    xpos = d3.scaleLinear().range([0, slwidth - thumbwidth]).domain([0,100]);
    mixstep = 1;
    mixpos = d3.scaleLinear().range([1, 100]).domain([thumbwidth, slwidth - thumbwidth]);
    

    d3.csv('/listmixer', function(error, data) {
      if(error) throw error;
      // 
      d3.select('#MIXER').selectAll('svg').remove();
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
                    d3.text('/setmixer')
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
    .html("<IMG ID='REPLIMG' SRC='" + img + "'><BR><CENTER>" + descr + "</CENTER>",function(){
      var theimg = d3.select("#REPLIMG").node().getBoundingClientRect();
      d3.select(id)
        .style('position','absolute')
        .style('top',thebody.height / 2 - ((theimg.height/2)))
        .style('left',thebody.width / 2  - ((theimg.width/2)))
        .style('visibility','visible')
        .style('display','block')
        .style('z-index','-1');
    });
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

function refreshHostList() {
  d3.text("/getdevices", function(error,data) {
    d3.select("#DEVICES")
      .html(data);
    d3.select("#DEVICES")
      .selectAll('tr')
      .on('mouseout', hideHostDetail)
      .on('mouseover', showHostDetail);
  });
}

function showHostDetail(the_host) {
  td = d3.select(this).select('td');
  if(td.empty())
    return;
  the_host = td.text();
  margin = {top: 20, bottom: 20, left: 20, right: 20};
  width = 700;
  itemheight = 20;
  cpudiv = d3.select("#HOSTINFO");
  cpudiv.selectAll('svg').remove();
  d3.json('/deviceinfo/' + the_host, function(error, data) {
    if(! data) return;
    cpudisplay = cpudiv.style('display','block').style('visibility','visible')
      .append('svg')
         .attr('width', width + margin.left + margin.right)
         .attr('height', itemheight * (Object.keys(data).length + 1) + margin.top + margin.bottom)
         .append('g')
           .attr('transform', 'translate(' + margin.left + ', ' + margin.top + ')');
    Object.keys(data).forEach(function(key, i) {
      nxttxt = cpudisplay.append('g')
        .attr('transform', 'translate(0, ' + (i + 1) * itemheight + ')');
      nxttxt.append('text')
        .text(key);
      nxttxt.append('text')
        .attr('x', '160')
        .text(data[key]);
    });
    cpudisplay.append('g').append('text')
      .attr("font-size", "20px")
      .text(the_host);
  });
}

function hideHostDetail() {
  d3.select("#HOSTINFO")
    .style('display','none')
    .style('visibility','hidden');
}
