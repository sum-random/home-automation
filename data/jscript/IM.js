window.onload = initAll;
var xhr = false;
var xPos, yPos;

function initAll() {
	var allLinks = document.getElementsByClassName("IMGCELL");

	for (var i=0; i< allLinks.length; i++) {
		allLinks[i].onmouseover = showPreview;
		allLinks[i].onmouseout = hidePreview;
	}
}

function hidePreview(evt) {
	var prevWin = document.getElementById("POPWIN");
	prevWin.style.visibility = "hidden";
}

function showPreview(evt) {
	if (evt) {
		var url = evt.target.src;
	}
	else {
		evt = window.event;
		var url = evt.srcElement.src;
	}

	xPos = evt.clientX;
	yPos = evt.clientY;

	var prevWin = document.getElementById("POPWIN");
	prevWin.innerHTML = "<IMG BORDER='5' SRC='" + url + "'>";
	prevWin.style.top = parseInt(yPos)-100+window.pageYOffset + "px";
	prevWin.style.left = parseInt(xPos)+15+window.pageXOffset + "px";
	prevWin.style.visibility = "visible";
}



