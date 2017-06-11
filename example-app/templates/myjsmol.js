Jmol._isAsync = false;
var jmolApplet0; // set up in HTML table, below
jmol_isReady = function(applet) {
document.title = (applet._id + " - Jmol " + Jmol.___JmolVersion)
// Jmol._getElement(applet, "appletdiv").style.border="10px solid blue"
}

var Info = {
   width: '100%',
   height: '100%',
   debug: false,
   color: "0xFFFFFF",
   use: "HTML5",   // JAVA HTML5 WEBGL are all options
   j2sPath: "{{dir}}/static/jmol/j2s", // this needs to point to where the j2s directory is.
   jarPath: "{{dir}}/static/jmol/java",// this needs to point to where the java directory is.
   jarFile: "JmolAppletSigned.jar",
   isSigned: true,
   script: "set antialiasDisplay;load {{dir}}/static/xyz/set.0000.xyz;" ,
   serverURL: "./jmol/php/jsmol.php",
   readyFunction: jmol_isReady,
   disableJ2SLoadMonitor: true,
   disableInitialConsole: true,
   allowJavaScript: true
};

$(document).ready(function() {
$("#appdiv").html(Jmol.getAppletHtml("jmolApplet0", Info))
});
var lastPrompt=0;

var JSmolCloneData = {};
function cloneJSmol(JSmolObject) {
  var t = JSmolObject._jmolType; //temp
  if ( /_Canvas2D/.test(t) ) { t = 'HTML5'; }
  else if ( /_Canvas3D/.test(t) ) { t = 'WebGL'; }
  else if ( /_Applet/.test(t) ) { t = 'Java'; }
  else { t = null; }
  JSmolCloneData.type = t;
  JSmolCloneData.platformSpeed = Jmol.evaluate(JSmolObject, 'platformSpeed + 0');
  JSmolCloneData.state = Jmol.getPropertyAsString(JSmolObject, 'stateInfo');
  var inds=localStorage.getItem("indexref") ;
  localStorage.setItem("index",inds);
  myWindow=window.open('{{dir}}/static/pop.html',inds,'resizable, width=800, height=800, scrollbars, menubars=no, titlebar=no,toolbar=no,location=no,status=yes');

};


var inds=localStorage.getItem("index");

function holdJSmol(JSmolObject){
   var t = JSmolObject._jmolType; //temp
   JSmolCloneData.type = 'HTML5';
   JSmolCloneData.state = Jmol.getPropertyAsString(JSmolObject, 'stateInfo');
   myWindow=window.open('{{dir}}/static/compare.html','compare','width=200, height=200, scrollbars, menubars=no');
   var inds=localStorage.getItem("indexref") ;
   localStorage.setItem("index",inds);

};
