// Headless smoke test of the walkthrough engine: a tiny DOM shim, then play it through.
const fs=require('fs'), path=require('path'); const B=path.join(__dirname,'build');
function CL(){const s=new Set();return{toggle(x,f){if(f===undefined)f=!s.has(x);f?s.add(x):s.delete(x);return f},add(...a){a.forEach(x=>s.add(x))},remove(...a){a.forEach(x=>s.delete(x))},contains:x=>s.has(x),_s:s}}
const byId={};
function mk(tag){const e={tagName:(tag||'div').toUpperCase(),children:[],_a:{},classList:CL(),style:{},type:'',title:'',parentNode:null,hidden:false,
  set className(v){e.classList._s.clear();v.split(' ').filter(Boolean).forEach(c=>e.classList.add(c))},get className(){return [...e.classList._s].join(' ')},
  set innerHTML(v){e._html=v; [...v.matchAll(/id="(m[bvdg]\d+|ml\d+)"/g)].forEach(x=>{const c=mk('span');c.id=x[1];byId[x[1]]=c;});},get innerHTML(){return e._html||''},
  textContent:'',setAttribute(k,v){e._a[k]=String(v)},getAttribute(k){return k in e._a?e._a[k]:null},
  appendChild(c){e.children.push(c);c.parentNode=e;return c},removeChild(c){e.children=e.children.filter(x=>x!==c);c.parentNode=null},
  get firstChild(){return e.children[0]||null},
  addEventListener(t,f){(e._h=e._h||{})[t]=f},querySelector(sel){return sel==='text'?e._text||null:mk('span')},dispatch(t){e._h&&e._h[t]&&e._h[t]({preventDefault(){},stopPropagation(){},target:{tagName:'DIV'}})},
  getBoundingClientRect(){return{top:0,bottom:10,left:0,right:10,width:800,height:600}},cloneNode(){return mk('g')},get offsetWidth(){return 1},get offsetHeight(){return 1},scrollIntoView(){},querySelectorAll(){return []}};return e;}
['fig','fx','frames','marks','pop','steps','ticks','play','prev','next','reset','showall','counter','sl-n','sl-t','sl-x','rh-v','metrics','m-rows','m-title','m-final'].forEach(i=>{byId[i]=mk();byId[i].id=i});
const cells=JSON.parse(fs.readFileSync(path.join(B,'cells.json'),'utf8')).meta, frag=fs.readFileSync(path.join(B,'fig.svgfrag'),'utf8');
const groups=[];
for(const k in cells){const g=mk('g');g.setAttribute('data-s','a:'+k);const b=cells[k].bb;g.setAttribute('data-bb',`${b[0]},${b[1]},${b[2]-b[0]},${b[3]-b[1]}`);
  const m=frag.match(new RegExp('data-s="a:'+k+'"[^>]*>(?:(?!</g>).)*?<text ([^>]*)>'));
  if(m){const t=mk('text'); for(const a of m[1].matchAll(/([\w-]+)="([^"]*)"/g)) t.setAttribute(a[1],a[2]); t._tspans=[]; t.appendChild=c=>{t._tspans.push(c);return c}; Object.defineProperty(t,'firstChild',{get(){return t._tspans[0]||null}}); t.removeChild=()=>t._tspans.shift(); g._text=t;}
  groups.push(g);}
byId.fig.querySelectorAll=sel=>sel==='g.el'?groups:[];
byId.pop.hidden=true; global.document={querySelectorAll(){return []},getElementById:id=>(byId[id]||(byId[id]=mk())),createElement:mk,createElementNS:(ns,t)=>mk(t),addEventListener(){},querySelector(s){return s==='.sheet'?mk('div'):null},fonts:null,body:mk('body')};
global.window={matchMedia:()=>({matches:false}),addEventListener(){},parent:null,onerror:null}; global.performance={now:()=>0}; global.location={search:'?embed=1'};
let T=[],R=[]; global.setTimeout=(f)=>{T.push(f);return T.length}; global.clearTimeout=()=>{};
global.requestAnimationFrame=(f)=>{R.push(f);return R.length}; global.cancelAnimationFrame=()=>{};
eval(fs.readFileSync(path.join(B,'page.js'),'utf8'));
const lit=()=>groups.filter(g=>g.classList.contains('lit')).length, dots=()=>byId.fx.children.filter(c=>c.classList.contains('dot')).length;
const txt=k=>{const g=groups.find(g=>g.getAttribute('data-s')==='a:'+k); return g&&g._text?g._text._tspans.map(t=>t.textContent).join(' | '):'(none)'};
console.log('showAll: lit',lit(),'/',groups.length,'| rail rows',byId.steps.children.filter(c=>c.classList.contains('beat')).length,'| ws-src:',txt('ws-src'),'| rev-2:',txt('rev-2'));
let now=0; function pump(){let guard=0; while((R.length||T.length)&&guard++<300000){ if(R.length){const f=R.shift(); now+=16; f(now);} else {T.shift()();} } return guard;}
byId.play.dispatch('click'); console.log('after play: dots',dots(),'lit',lit(),'counter',byId.counter.textContent,'| h-analysis:',txt('h-analysis'));
const g=pump();
console.log('after full run: steps',g,'| lit',lit(),'| counter',byId.counter.textContent,'| fig all',byId.fig.classList.contains('all'),'| metrics on',byId.metrics.classList.contains('on'),'| ripples left',byId.fx.children.filter(c=>c.classList.contains('ripple')).length);
const BE=byId.steps.children.filter(c=>c.classList.contains('beat'));
BE[6].dispatch('click'); pump(); console.log('beat07 rev-001: metrics',byId['m-title'].textContent,'| mv0',byId.mv0.textContent,'| rev-1:',txt('rev-1'),'| rev-2:',txt('rev-2'),'| marks',byId.marks.children.length,'| frames',byId.frames.children.map(f=>f.getAttribute('class')));
BE[10].dispatch('click'); pump(); console.log('beat11 rev-2: metrics',byId['m-title'].textContent,'| mv0',byId.mv0.textContent,'delta',byId.md0.textContent,byId.md0.classList.contains('on'),'| h-impl:',txt('h-impl'),'| tab:',txt('h-impl-tab'),'| h-rev:',txt('h-rev'));
BE[13].dispatch('click'); pump(); console.log('beat14 rev-4: ws-src:',txt('ws-src'),'| rev-2:',txt('rev-2'),'| mv1',byId.mv1.textContent,'mv2',byId.mv2.textContent);
BE[16].dispatch('click'); pump(); console.log('beat17 verifier: metrics',byId['m-title'].textContent,'| marks',byId.marks.children.map(m=>m.getAttribute('class')).join(','),'| final',byId['m-final'].innerHTML.replace(/<[^>]+>/g,' ').replace(/\s+/g,' ').trim().slice(0,140));
BE[0].dispatch('click'); pump(); console.log('beat01: lit',lit(),'| faded',groups.filter(g=>g.classList.contains('faded')).length,'| ws-src:',txt('ws-src'),'| metrics on',byId.metrics.classList.contains('on'));
