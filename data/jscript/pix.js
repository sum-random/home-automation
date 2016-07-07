window.onload = initAll;
var xhr = false;
var xPos, yPos, pyo, pxo;
var url;

function initAll() {
	var allLinks = document.getElementsByTagName("img");

	for (var i=0; i< allLinks.length; i++) {
		if(allLinks[i].id == "IMGCELL") {
			allLinks[i].onmouseover = showPreview;
			allLinks[i].onmouseout = hidePreview;
		}
	}
}

function hidePreview(evt) {
	var prevWin = document.getElementById("POPWIN");
	prevWin.style.visibility = "hidden";
}

function showPreview(evt) {
	if (evt) {
		url = evt.target.src;
        	var tot = evt.target.offsetTop;
        	var tol = evt.target.offsetLeft;
        	var twd = evt.target.offsetWidth;
        	var tht = evt.target.offsetHeight;
		pyo = window.pageYOffset;
		pxo = window.pageXOffset;
	}
	else {
		evt = window.event;
		url = evt.srcElement.src;
        	var tot = evt.srcElement.offsetTop;
        	var tol = evt.srcElement.offsetLeft;
        	var twd = evt.srcElement.offsetWidth;
        	var tht = evt.srcElement.offsetHeight;
		pyo = document.body.scrollTop;
		pxo = document.body.scrollLeft;
	}

	xPos = evt.clientX;
	yPos = evt.clientY;
        sfact=4;
         
	var prevWin = document.getElementById("POPWIN");
	prevWin.style.position="absolute";
	var pwt = window.pageYOffset;
	prevWin.style.top = "0px";
	prevWin.style.left = "0px";
	prevWin.innerHTML = "<IMG ID='PWIMG' WIDTH='40%' HEIGHT='40%' BORDER='5' SRC='" + url.replace("thumbsize","websize") + "'>";
	var pwImg = document.getElementById("PWIMG");
        pwImg.onload=function() {
          var prevWin = document.getElementById("POPWIN");
          var pwImg = document.getElementById("PWIMG");
	  var xOff=20;
	  var yOff=20;
          if(yPos > screen.availHeight*.4) { yOff=-10-(pwImg.height*1.1); }
          if(xPos > screen.availWidth/2) { xOff=-10-(pwImg.width*1.1); }
	  prevWin.style.top = yPos+pyo+yOff + "px";
	  prevWin.style.left = xPos+pxo+xOff + "px";
	  prevWin.style.visibility = "visible";
        }

}



