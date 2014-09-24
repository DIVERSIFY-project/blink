/* This script is inspired by what has been done by
Peter Eckersley and the Electronic Frontier Foundation
on https://panopticlick.eff.org/ */

var userAgent = window.navigator.userAgent;
var platform = window.navigator.platform;
var cookieEnabled = window.navigator.cookieEnabled;
var doNotTrack = "";
if (window.navigator.doNotTrack && (window.navigator.doNotTrack == "yes" || window.navigator.doNotTrack == "no")){
	doNotTrack = window.navigator.doNotTrack;
} else {
	doNotTrack = "NC";
}

var timezone = new Date().getTimezoneOffset();
var resolution = window.screen.availWidth+"x"+window.screen.availHeight+"x"+window.screen.colorDepth;

//Enumeration of navigator.plugins
var plugins = "";
if (window.navigator.plugins) {
	var np = window.navigator.plugins;
	var plist = new Array();
	for (var i = 0; i < np.length; i++) {
	  plist[i] = np[i].name + "; ";
	  plist[i] += np[i].description + "; ";
	  plist[i] += np[i].filename;
	  for (var n = 0; n < np[i].length; n++) {
	  	plist[i] += " (" + np[i][n].description +"; "+ np[i][n].type +
	  		       "; "+ np[i][n].suffixes + ")";
	  }
	  plist[i] += ". ";
	}
	plist.sort(); 
	for (i = 0; i < np.length; i++)
	  plugins+= "Plugin "+i+": " + plist[i];
}

//Canvas fingerprinting
canvas = document.createElement("canvas");
canvasContext = canvas.getContext("2d");
canvas.style.display = "inline";
canvasContext.textBaseline = "alphabetic";
canvasContext.fillStyle = "#f60";
canvasContext.fillRect(125, 1, 62, 20);
canvasContext.fillStyle = "#069";
canvasContext.font = "11pt no-real-font-123";
canvasContext.fillText("Cwm fjordbank glyphs vext quiz, \ud83d\ude03",2,15);
canvasContext.fillStyle = "rgba(102, 204, 0, 0.7)";
canvasContext.font =  "18pt Arial";
canvasContext.fillText("Cwm fjordbank glyphs vext quiz, \ud83d\ude03",4,17);
canvasData = canvas.toDataURL();

try {
	ieUserData = "";
    oPersistDiv.setAttribute("testStorage", "value remembered");
    oPersistDiv.save("oXMLStore");
    oPersistDiv.setAttribute("testStorage", "overwritten!");
    oPersistDiv.load("oXMLStore");
	if ("value remembered" == (oPersistDiv.getAttribute("testStorage"))) {
      ieUserData= "yes";
	} else { 
     ieUserData = "no";
	}
} catch (ex) {
     ieUserData = "no";
 }

try { 
    localStorage.fp = "test";
    sessionStorage.fp = "test";
} catch (ex) { 
}

try {
	domLocalStorage = "";
    if (localStorage.fp == "test") {
       domLocalStorage = "yes";
    } else {
       domLocalStorage = "no";
    }
} catch (ex) { 
	domLocalStorage = "no"; 
}

try {
	domSessionStorage = "";
    if (sessionStorage.fp == "test") {
       domSessionStorage = "yes";
    } else {
       domSessionStorage = "no";
    }
} catch (ex) { 
	domSessionStorage = "no"; 
}
