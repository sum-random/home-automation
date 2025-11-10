function setupWeather() {
  d3.selectAll('.weatherthumb')
    .on('mouseover', showWImg);

  thediv = d3.select('#WEATHERIMG');
  thediv.select('svg').remove();
  thediv.append('svg').append('svg:image')
    .attr('width', '90%')
    .attr('class', 'weatherShow');

  var temps = d3.select('#TEMPERATURES');
  temps.selectAll('svg').remove();
  var svg=temps.append('svg');
  svg.append('g').attr('id','graph')//graph
    .on('doubleclick',function(){
      d3.select(this).selectAll('path')
        .style('opacity','100%');
    });
  svg.append('g').attr('id','vscale');//vscale
  svg.append('g').attr('id','hscale');//hscale
  svg.append('g').attr('id','legend').append('rect');//legend
  cpuTemperatureGraph();
  setInterval(cpuTemperatureGraph,300000);
  d3.select(window).on('resize', resizeGraph);
  d3.select('#FORECASTGRAPH')
    .attr('width',90)
    .attr('height',64)
    .append('g');
  //setInterval(forecastGraph,3600000);
  forecastGraph();
}

function forecastGraph() {
  var fccontainer = d3.select('#FORECASTGRAPH');
  var fcthumb = d3.select('#FORECASTGRAPH').select('g');
  //fcthumb.width = 64;
  //fcthumb.height= 64;

  d3.csv('/getforecast')
    .then(function(fcdata){
      var locations=[];
      var graphdata = d3.groups(fcdata, d => d.location);
      Array.from(graphdata).forEach(function(d){locations.push(d[0]);});
      console.log(locations);
      var color = d3.scaleOrdinal()
        .domain(locations.sort())
        .range(['#aa0000','#aaaa00', '#0000ff', '#ff00ff', '#000000', '#ffaaff', '#aa00ff', '#00aa00', '#00aaff', '#aa5500', '#55aa00', '#555500']);
      var vscale = d3.scaleLinear()
        .domain(d3.extent(fcdata, d => d.temperature))
        .range([fccontainer.attr('height'),0]);
      var hscale = d3.scaleTime()
        .domain(d3.extent(fcdata, function(d) {return new Date(d.time);}))
        .range([0,fccontainer.attr('width')]);
      var linefunc =  d3.line()
        .x(function(d){return hscale(new Date(d.time));})
        .y(function(d){return vscale(d.temperature);});
      fcthumb.selectAll('path')
        .data(graphdata)
        .enter().append('path')
          .attr('fill', 'none')
          .attr('stroke', function(d) {return color(d[0]);})
          .attr('stroke-width', 3)
          .attr('d',function(d){return linefunc(d[1]);});
      fcthumb.selectAll('path')
        .exit().remove();
    });
  
}
function resizeGraph(arg) {
  var margins = 50;
  var graphx = window.innerWidth - margins*2;
  var graphy = window.innerHeight - margins*2;
  if(graphx<640) graphx=640;
  if(graphy<480) graphy=480;

  var temps = d3.select('#TEMPERATURES');
  var base = temps.select('svg')
      .attr('width', graphx)
      .attr('height',graphy);
  var svg = base.selectAll('g');
  svg.each(function(d,i) {
    gbox=d3.select(this);
    switch(gbox.attr('id')) {
      case 'graph':
        gbox.attr('width', graphx-margins*2)
            .attr('height', graphy)
            .attr('transform',
                  'translate('+margins+',0)');      
        break;
      case 'vscale':
        gbox.attr('width', margins)
            .attr('height', graphy)
            .attr('transform', 'translate('+margins+',0)');
        break;
      case 'hscale':
        gbox.attr('width', graphx)
            .attr('height', margins)
            .attr('transform', 'translate('+margins+','+(graphy-margins)+')');
        break;
      case 'legend':
        gbox.attr('width',margins)
            .attr('height',graphy-margins*2)
            .attr('text-anchor','top')
            .attr('transform','translate('+(graphx-margins)+',0)');
        break;
    }
  });
  if (typeof arg !== 'undefined')
    cpuTemperatureGraph(false);
}

// show cpu temperature graphs for last 48 hours
function cpuTemperatureGraph(doResize=true) {
  var margins = 50;
  var queryx = window.outerWidth;
  var graphx = window.innerWidth - margins*2;
  var graphy = window.innerHeight - margins;
  if(graphx<640) graphx=640;
  if(graphy<480) graphy=480;

  var temps = d3.select('#TEMPERATURES');
  var base = temps.select('svg');
  var svg = base.selectAll('g');
  if(doResize)
    resizeGraph();

  // read data
  first_time = Math.floor(Date.now()/1000 - queryx * 300);
  start_time = Math.floor(Date.now()/1000 - graphx * 300);
  d3.csv('/getweather?start='+first_time+'&pixels='+graphx, {method: "get"})
    .then(function(dataRaw) {
      var data=dataRaw.filter((d) => d.timestamp>=start_time);
      var vscale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.mavg))
        .range([graphy-margins*2,0]);
      var hscale = d3.scaleLinear()
        .domain(d3.extent(data, d => d.timestamp))
        .range([0,graphx-margins*2]);
      var tscale = d3.scaleTime()
        .domain(d3.extent(data, function(d) { return new Date(d.timestamp*1000);}))
        .range([0,graphx-margins*2]);
      var linefunc = d3.line()
        //break the line where there are data gaps
        .defined(function(d,i,a) {return (i==0 || i==a.length-1 || d.timestamp-a[i-1].timestamp==a[i+1].timestamp-d.timestamp);})
        .x(function(d){return hscale(d.timestamp);})
        .y(function(d){return vscale(d.mavg);});
      var hostfunc = d3.group(data, d => d.host);
      var color = d3.scaleOrdinal()
        .domain(hostfunc.keys())
        .range([ '#aa0000','#aaaa00', '#0000ff', '#ff00ff', '#000000', '#ffaaff', '#aa00ff', '#00aa00', '#00aaff', '#aa5500', '#55aa00', '#555500']);
      //svg.data(hostfunc);
      svg.each(function(d,i) {
        gcon=d3.select(this);
        switch(gcon.attr('id')) {
          case 'graph':
            if(!doResize) //window size changed, blow away lines to refresh data
              gcon.selectAll('path').remove();
            gcon.selectAll('path')
              .data(hostfunc)
              .enter().append('path')
                .attr('stroke', function(d) {return d3.color(color(d[0]));})
                .attr('fill', 'none')
                .attr('stroke-width', 3)
                //.on('mouseover',function(d){d3.select('#'+d3.select(this).attr('id')).raise();})
                .on('mouseover',function(d){d3.select(this).raise();})
                .on('click',function(){d3.select('#'+d3.select(this).attr('id')).style('opacity','25%');})
                .attr('id', function(d) {return d[0];})
                .attr('d', function(d) {return linefunc(d[1]);});
            gcon.selectAll('path').exit().remove();
            break;
          case 'vscale':
            gcon.call(d3.axisLeft(vscale));
            break;
          case 'hscale':
            gcon.call(d3.axisBottom(tscale));
            break;
          case 'legend':
            lbg = gcon.select('rect')
              .attr('height',graphy-margins*2)
              .attr('width',margins);
            if(!doResize) //window size changed, blow away labels to refresh data
              gcon.selectAll('text').remove();
            gcon.selectAll('text')
              .data(hostfunc)
              .attr('fill','none')
              .enter().append('text')
                .text(function(d,i,a) {return d[0];})
                .attr('value',function(d) {return d.host;})
                .style("font-size",function(d) {fs=22-d[0].length*1.5;return fs+"px";})
                .attr('x',5)
                .attr('y', function(temps){var t = temps[1]; return vscale(t[t.length-1].mavg);})
                .attr('id',function(d) {return d[0];})
                .on('mouseover',function(d){d3.select('#'+d3.select(this).attr('id')).raise();})
                .on('click',function(){d3.select('#'+d3.select(this).attr('id')).style('opacity','85%');})
                .attr('fill',function(d) {return d3.color(color(d[0])).brighter();})
                .attr('stroke',function(d) {return d3.color(color(d[0])).darker();})
                .attr('stroke-width','0.5');
            gcon.selectAll('text').exit().remove();
            if(doResize)
              d3.json('/getagw')
                .then(function(data){lbg.attr('fill','rgba('+data.status[0]+','+data.status[1]+',32)');});
            break;
          default:
        }
      });
  });
}

function showOneLightSchedule() {
    thelight = d3.select("#PICKALIGHT").node().value;
    the_display = d3.select("#LIGHTSCHED").select("#SCHEDLIST");
    if(thelight > -1) {
        d3.tsv('/getonelightsched/' + thelight).then(function(rawdata) {
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
        d3.json('/getlightscheddetail/' + the_item).then(function(data) {
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
    d3.text('/setlightscheddetail',{method: 'post', body: 'the_id='+d3.select('#SCHEDLIST').node().value+'\nthe_hhcode=I\nthe_lightcode='+d3.select('#PICKALIGHT').node().value+'\nthe_month='+d3.select('#MONTHMATCH').node().value+'\nthe_day='+d3.select('#DAYMATCH').node().value+'\nthe_on_time='+d3.select('#TURNON').node().value+'\nthe_off_time='+d3.select('#TURNOFF').node().value+'\nnew_item='+(newItem?'true':'false')+'\n'}).then(function(data) {
        showOneLightSchedule();
        showScheduleItem();
       });
}

function deleteScheduleItem() {
    d3.json('/deletelightscheddetail')
        .post('the_id='+d3.select('#SCHEDLIST').node().value).then(function(data) {
            showOneLightSchedule();
       });

}

function populateMusicList() {
    thetextfield = document.getElementById("TUNEFILTER");
    thetext = thetextfield.value;
    thelistdisplay = d3.select("#MUSICDIV").select("#TUNELIST");
    if(thetext.length > 3) {
        d3.csv('/getmusic?filter=' + thetext).then(function(rawdata) {
            data = rawdata.sort(function(d){return d.shortname;})
            theoptions = thelistdisplay.selectAll("option").data(data, function(d){return d.shortname;});
            theoptions.exit().remove();
            theoptions.enter().append("option");
            thelistdisplay.selectAll("option")
              .attr('value', function(d) {return d.fileid;})
              .text(function(d) {return d.shortname;});
            thelistdisplay.attr("size", Math.min(data.length,25));
        });
    } else {
        thelistdisplay.selectAll("option").remove();
        thelistdisplay.attr("size", 4);
    }
}

function refreshPlayList() {
    theplaylistfield = d3.select("#MUSICDIV").select("#PLAYLIST");
    d3.csv('/getplaylist').then(function(playlistdata) {
        theoptions = theplaylistfield.selectAll('option').data(playlistdata, function(d){return d.shortname;});
        theoptions.exit().remove();
        theoptions.enter().append("option");
        theplaylistfield.selectAll("option")
            .attr('value', function(d) {return d.fileid;})
            .text(function(d) {return d.shortname;});
        theplaylistfield.attr("size", Math.min(playlistdata.length,25));
    });
}

function addtunes() {
    idlist=[];
    optlist = d3.select("#MUSICDIV").select("#TUNELIST").selectAll("option")
        .filter(function(d,i) { return this.selected;}).nodes();
    optlist.forEach(function(d) {idlist.push(d.value);});
    d3.text('/addplaylist', {method: 'post', body: "fileid="+JSON.stringify(idlist)}).then(function(d) {refreshPlayList();});
}

function rmtunes() {
    idlist = [];
    optlist = d3.select("#MUSICDIV").select("#PLAYLIST").selectAll("option")
        .filter(function(d,i) { return this.selected;}).nodes();
    optlist.forEach(function(d) {idlist.push(d.value);});
    d3.text('/rmplaylist',{method: 'post', body: "fileid="+JSON.stringify(idlist)}).then(function() {refreshPlayList();});
}

function musiccontrol() {
    d3.select("#MUSICDIV").selectAll('svg').remove();
    btndata = [ { x: 3,  y:  2, w: 67, h: 17, p: "34,5 34,17 40,11"}, //play
                { x: 3,  y: 24, w: 19, h: 17, p: "7,26 7,37 9,37 9,32 14,37 14,32 19,37 19,26 14,30 14,26 9,30 9,26"}, //rw to start
                { x: 27, y: 24, w: 19, h: 17, p: "37,26 32,31 37,37 37,32 42,37 42,26 37,30"}, //rewind
                { x: 52, y: 24, w: 19, h: 17, p: "58,26 58,37 63,32 63,37 68,31 63,26 63,30 "}, //fast forward
                { x: 77, y: 24, w: 19, h: 17, p: "81,26 81,37 86,32 86,37 91,32 91,37 93,37 93,26 91,26 91,30 86,26 86,30"}, //next track
                { x: 77, y: 2,  w: 19, h: 17, p: ["83,8 83,16 85,16 85,8","88,8 88,16 90,16 90,8"]}, //pause
                { x:100, y: 2,  w: 19, h: 17, p: "107,7 113,7 113,14 107,14"}, //stop
                { x:100, y: 24, w: 19, h: 17, p: ["107,31 111,27 115,31 107,31","107,33 115,33 115,34 107,34 107,33"]}]; // eject
    canvas = d3.select("#MUSICDIV").append('svg')
        .attr('width',388)
        .attr('height',167)
        .append('g');
    buttonpad = canvas.append('g')
        .attr('transform', 'translate(117,83)');
    btndata.forEach(function(d,i) {
        btnbody = canvas.append('rect')
            .attr('x',d.x)
            .attr('y',d.y)
            .attr('width',d.w)
            .attr('height',d.h)
            .style('fill',d3.rgb(191,191,191));
        btnsymbol = canvas.append("polygon")
            .attr("points", d.p)
            .style("fill", "black")
            .style("stroke", "none")
            .style("strokeWidth", "0px");
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
    [ '#PIX', '#FULLSZ', '#MIXER', '#LIGHTS', '#PLACES', '#WEATHER', '#DEVICES', '#BOOKMARKS', '#MASTODON', '#MUSICDIV', '#LIGHTSCHED','#TEMPERATURES' ].forEach(function(d) {
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
    d3.json("/getimages",{'method': 'post', 'body': "the_folder_id="+fldr})
        .then(function(data) {
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
                .on('mouseenter', function(d,i) {
                    d3.select(this)
                        .attr("border", "1px,green");
                    expandImage("/thumbnail?IMGID="+d.imgid);
                });
            });
        });
}

function expandImage(uri) {
    evt = window.event;
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
    d3.csv('/listlight').then(function(data) {
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
}
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
    d3.text('/setlight',{method: 'post', body: 'DEV=' + theidx + '\nSTATE=' + thestate}).then(function(d) {  console.log(d);});
     
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

    d3.csv('/listmixer').then(function(data) {
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
            .attr('id', 'slider' + d.device)
            .style('fill', '#C0C0C0');
        slider.append('text')
            .attr('x', slwidth / 2)
            .attr('y', slheight / 2)
            .attr('enabled', false)
            .attr('fill', 'black')
            .attr('text-anchor', 'middle')
            .attr('id', 'label' + d.device)
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
        function startDrag(event) {
            this.candrag = true;
            this.vp = mixstep * parseInt(mixpos(d3.pointer(event)[0])/mixstep);
            thethumb = d3.select('#thumb' + this.id);
            thethumb.attr('style', 'fill: rgba(255,0,0,1);');
        }
        function endDrag() {
            thethumb = d3.select('#thumb' + this.id);
            this.candrag = false;
            thethumb.attr('style', 'fill: rgba(255,0,0,0.50);');
        }
        function dragIt(event) {
            thethumb = d3.select('#thumb' + this.id);
            if(this.candrag){
                var mx = d3.pointer(event)[0];
                var vp = parseInt(mixpos(mx)/mixstep)*mixstep;
                vp = (vp>100?100:vp<0?0:vp);
                var tp = xpos(vp);
                thethumb.attr("x", tp);
                if(this.vp != vp) {
                    this.vp = vp;
                    d3.text('/setmixer', {method: 'post', body: 'DEV=' + this.id + '\nVALUE=' + vp});
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
        if (typeof url == 'undefined'){
            var margins=50;
            var pw = d3.select(prevWin);
            var graphx = window.innerWidth - margins*2;
            var graphy = window.innerHeight - margins*2;
            if(graphx<640) graphx=640;
            if(graphy<480) graphy=480;
            pw.selectAll('img').remove();
            pw.selectAll('svg').remove();
            cleanwin = pw.append('svg')
              .attr('width',graphx)
              .attr('height',graphy);
            fcfull = cleanwin.append('g')
              .attr('id','fcfull')
              .attr('width', graphx-margins*2)
              .attr('height', graphy-margins)
              .attr('transform',
                    'translate('+margins+',0)');      
            vscalecontainer = cleanwin.append('g')
              .attr('id','vscale')
              .attr('width', margins)
              .attr('height', graphy-margins)
              .attr('transform', 'translate('+margins+',0)');
            hscalecontainer = cleanwin.append('g')
              .attr('id','hscale')
              .attr('width', graphx-margins*2)
              .attr('height', margins)
              .attr('transform', 'translate('+margins+','+(graphy-margins*2)+')');
            legend = cleanwin.append('g')
              .attr('id','legend')
              .attr('width',margins)
              .attr('height',graphy-margins*2)
              .attr('text-anchor','top')
              .attr('transform','translate('+(graphx-margins)+',0)');
            d3.csv('/getforecast')
              .then(function(rawdata){
                locations=[];
                var graphdata = d3.groups(rawdata, d => d.location);
                Array.from(graphdata).forEach(function(d){locations.push(d[0]);});
                var color = d3.scaleOrdinal()
                  .domain(locations.sort())
                  .range([ '#aa0000','#aaaa00', '#0000ff', '#ff00ff', '#000000', '#ffaaff', '#aa00ff', '#00aa00', '#00aaff', '#aa5500', '#55aa00', '#555500']);
                var vscale = d3.scaleLinear()
                  .domain(d3.extent(rawdata, d => d.temperature))
                  .range([graphy-margins*2-1,0]);
                var hscale = d3.scaleTime()
                  .domain(d3.extent(rawdata, function(d) {return new Date(d.time);}))
                  .range([0,graphx-margins*2-1]);
                var linefunc =  d3.line()
                  .x(function(d){return hscale(new Date(d.time));})
                  .y(function(d){return vscale(d.temperature);});
                fcfull.selectAll('path')
                  .data(graphdata)
                  .enter().append('path')
                    .attr('fill', 'none')
                    .attr('stroke', function(d) {return color(d[0]);})
                    .attr('stroke-width', 3)
                    .attr('d',function(d){return linefunc(d[1]);});
                fcfull.selectAll('path')
                  .exit().remove();
                vscalecontainer.call(d3.axisLeft(vscale));
                hscalecontainer.call(d3.axisBottom(hscale));
                legend.selectAll('text')
                  .data(graphdata)
                  .enter().append('text')
                    .attr('x',5)
                    .attr('y',function(d){return vscale(d[1][d[1].length-1].temperature);})
                    .attr('fill', d3.color('black'))
                    .attr('stroke', function(d) {return color(d[0]);})
                    .attr('stroke-width', 1)
                    .attr('value',function(d) {return d[0];})
                    .style("font-size",function(d) {fs=22-d[0].length*1.5;return fs+"px";})
                    .text(function(d){return d[0];});
              });
        } else {
            prevWin.innerHTML = "<CENTER><IMG BORDER='5' SRC='" + url + "' CLASS='weathershow'></CENTER>";
        }
        prevWin.style.visibility = "visible";
}

function hideWImg(evt) {
        var prevWin = document.getElementById("WEATHERIMG");
        prevWin.style.visibility = "hidden";
}

function refreshHostList() {
  d3.text("/getdevices").then(function(data) {
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
  d3.json('/deviceinfo/' + the_host).then(function(data) {
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
