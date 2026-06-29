// Model × Agent — deck behavior: scale-to-fit · arrow nav · build-up steps · presenter notes (N)
const params=new URLSearchParams(location.search);
const FULL=params.has('full');   // reveal all steps (screenshots / export)
const CLEAN=params.has('clean'); // hide nav chrome for clean capture
const deckEl=document.querySelector('.deck');
const slides=document.querySelectorAll('.slide');

const base=parseInt((deckEl&&deckEl.dataset.start)||'1',10);
slides.forEach((s,i)=>{const sn=s.querySelector('.snum');if(sn)sn.textContent=String(base+i).padStart(2,'0');});

if(!FULL)document.body.classList.add('stepping');
function stepsIn(s){return [...new Set([...s.querySelectorAll('[data-step]')].map(e=>+e.dataset.step))].sort((a,b)=>a-b);}
function showSteps(s,upto){s.querySelectorAll('[data-step]').forEach(e=>{e.classList.toggle('on',FULL||(+e.dataset.step)<=upto);});}

const tot=document.getElementById('tot');if(tot)tot.textContent=slides.length;
let idx=0,step=0;
function activate(n){slides[idx].classList.remove('active');idx=Math.max(0,Math.min(n,slides.length-1));const s=slides[idx];s.classList.add('active');step=0;showSteps(s,0);const c=document.getElementById('cur');if(c)c.textContent=idx+1;}
function next(){const s=slides[idx];const st=stepsIn(s);if(!FULL&&step<st.length){step++;showSteps(s,st[step-1]);}else activate(idx+1);}
function prev(){const s=slides[idx];if(!FULL&&step>0){step--;const st=stepsIn(s);showSteps(s,step>0?st[step-1]:0);}else activate(idx-1);}
showSteps(slides[0],0);

function fromHash(){const h=parseInt((location.hash||'').replace('#',''),10);if(!isNaN(h))activate(h-1);}
fromHash();window.addEventListener('hashchange',fromHash);

document.addEventListener('keydown',e=>{
  if(e.key==='ArrowRight'||e.key===' ')next();
  if(e.key==='ArrowLeft')prev();
  if(e.key==='n'||e.key==='N')document.body.classList.toggle('shownotes');
});

function fit(){const s=Math.min(window.innerWidth/1920,window.innerHeight/1080);if(deckEl)deckEl.style.transform='scale('+s+')';}
window.addEventListener('resize',fit);fit();

if(CLEAN){const nh=document.querySelector('.navhint');if(nh)nh.style.display='none';}
