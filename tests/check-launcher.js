// Run the complete shipped ES5 app against a small offline DOM and service stub.
'use strict';
var assert=require('assert'),fs=require('fs'),vm=require('vm'),path=require('path');
var source=fs.readFileSync(path.join(__dirname,'../app/home.js'),'utf8');
function start(config,seed){
 var elements={},events={},storage={},timers=[],launches=[];
 function element(tag){
  var e={tagName:tag,children:[],style:{},className:'',attributes:{},textContent:'',offsetTop:0,offsetHeight:191,scrollTop:0,clientHeight:540};
  e.classList={add:function(c){if(!e.classList.contains(c))e.className+=' '+c;},remove:function(c){e.className=e.className.split(' ').filter(function(x){return x!==c;}).join(' ');},contains:function(c){return e.className.split(' ').indexOf(c)>=0;},toggle:function(c,on){if(on)e.classList.add(c);else e.classList.remove(c);}};
  e.setAttribute=function(k,v){e.attributes[k]=v;};e.getAttribute=function(k){return e.attributes[k];};
  e.appendChild=function(c){c.parentNode=e;e.children.push(c);};
  e.getBoundingClientRect=function(){return {width:338,height:191,left:218,top:480};};
  e.click=function(){if(e.onclick)e.onclick();};
  Object.defineProperty(e,'innerHTML',{set:function(){e.children=[];}});
  return e;
 }
 ['actions','dock','apps','selection','focus','scroll','clock','greeting','date','weather','weather-credit','wallpaper','saver-clock','modal','modal-title','modal-hint','modal-items','saver','slide-a','slide-b','toast'].forEach(function(id){elements[id]=element('div');});
 elements.actions.children=[element('button'),element('button')];
 var body=element('body');
 var context={window:{HOME_CONFIG:config,SEED_APPS:seed,close:function(){launches.push(true);}},document:{body:body,hidden:false,getElementById:function(id){return elements[id];},createElement:element,querySelectorAll:function(){return [];},addEventListener:function(name,fn){events[name]=fn;}},localStorage:{getItem:function(k){return storage[k]||null;},setItem:function(k,v){storage[k]=v;}},setTimeout:function(fn){timers.push(fn);return timers.length;},clearTimeout:function(){},setInterval:function(){return 1;},clearInterval:function(){}};
 vm.createContext(context);vm.runInContext(source,context);
 function key(k){events.keydown({keyCode:k,preventDefault:function(){}});}
 return {elements:elements,body:body,key:key,events:events,storage:storage,timers:timers};
}
var apps=['a','b','c','d','e','f','g','h','i','j','k','kids'].map(function(id){return {id:id,title:id.toUpperCase(),packagedIcon:'assets/'+id+'.png'};});
var home=start({dock:['a','b','c','d'],hiddenApps:['kids'],banners:{a:'assets/banner-a.png'}},apps);
assert.equal(home.elements.dock.children.length,4);
assert.equal(home.elements.apps.children.length,7);
assert.equal(home.elements.dock.children[0].style.backgroundImage,'url("assets/banner-a.png")');
assert(!home.body.classList.contains('apps-open'));
home.key(40);assert(home.body.classList.contains('apps-open'));assert.equal(home.elements.selection.textContent,'E');
home.key(40);assert.equal(home.elements.selection.textContent,'I','Down uses four-column rows');
home.key(39);home.key(39);home.key(39);assert.equal(home.elements.selection.textContent,'K','Short final row clamps focus');
home.key(38);home.key(38);assert(!home.body.classList.contains('apps-open'));
// The actual long-OK handler must open arrangement controls without launching.
home.events.keydown({keyCode:13,preventDefault:function(){}});home.timers[home.timers.length-1]();
assert.equal(home.elements['modal-title'].textContent,'C');
assert.equal(home.elements['modal-items'].children.length,5);
home.events.keyup({keyCode:13});
var emptyDock=start({dock:[],hiddenApps:[]},apps);
assert.equal(emptyDock.elements.selection.textContent,'A');assert(emptyDock.body.classList.contains('apps-open'));
emptyDock.key(38);assert(!emptyDock.body.classList.contains('apps-open'));emptyDock.key(40);assert(emptyDock.body.classList.contains('apps-open'));
var empty=start({dock:[],hiddenApps:['a']},[{id:'a',title:'A'}]);
assert.equal(empty.elements.apps.children.length,0);empty.key(40);empty.key(38);
assert(!empty.body.classList.contains('apps-open'),'Top controls remain usable with no apps');
console.log('PASS: four-column navigation, banner override, hidden apps, long OK, empty dock and empty inventory');
