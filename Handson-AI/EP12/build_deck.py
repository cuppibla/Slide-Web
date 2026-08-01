"""Combine the individual Act slides into one self-contained, paginated deck
(slides_act2/index.html). Each slide's full HTML is inlined as a base64 data-URI
iframe — zero CSS collisions, pixel-perfect, single portable file.

Re-run after editing any slide:  python3 build_deck.py
"""
import base64
import glob
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "index.html")

files = sorted(
    f for f in glob.glob(os.path.join(HERE, "*.html"))
    if os.path.basename(f) != "index.html"
)

slides = []
for path in files:
    html = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    label = title.group(1).strip() if title else os.path.basename(path)
    num = re.search(r'class="slide-num">([^<]+)<', html)
    badge = num.group(1).strip() if num else ""
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    slides.append({"label": label, "badge": badge, "b64": b64,
                   "file": os.path.basename(path)})

print(f"bundling {len(slides)} slides:")
for i, s in enumerate(slides):
    print(f"  {i+1:2d}. [{s['badge']:>4}] {s['label']}")

# Build the JS array of slides
js_slides = ",\n".join(
    "{{badge:{b},label:{l},src:'data:text/html;base64,{d}'}}".format(
        b=repr(s["badge"]), l=repr(s["label"]), d=s["b64"])
    for s in slides
)

doc = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Episode 5 — Data Agent Kit · Deck</title>
<style>
  *{margin:0;padding:0;box-sizing:border-box}
  html,body{height:100%;background:#202124;font-family:'Google Sans',system-ui,sans-serif;overflow:hidden}
  #stage{position:fixed;inset:0;overflow:hidden}
  #wrap{position:absolute;left:50%;top:50%;width:1920px;height:1080px;transform-origin:center center;box-shadow:0 20px 80px rgba(0,0,0,.5);background:#fff;border-radius:6px;overflow:hidden}
  iframe{width:1920px;height:1080px;border:0;display:block}
  /* HUD */
  #hud{position:fixed;left:0;right:0;bottom:0;height:46px;display:flex;align-items:center;gap:16px;
       padding:0 22px;color:#E8EAED;font-size:13px;background:linear-gradient(180deg,rgba(32,33,36,0) 0%,rgba(32,33,36,.9) 60%);
       opacity:0;transition:opacity .25s;z-index:10}
  #stage:hover ~ #hud,#hud:hover{opacity:1}
  #title{font-weight:500;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}
  #count{font-variant-numeric:tabular-nums;color:#9AA0A6}
  .nav{cursor:pointer;color:#8AB4F8;font-weight:500;user-select:none;padding:4px 8px;border-radius:6px}
  .nav:hover{background:rgba(138,180,248,.15)}
  /* progress dots */
  #dots{position:fixed;left:50%;transform:translateX(-50%);bottom:54px;display:flex;gap:7px;z-index:10;opacity:0;transition:opacity .25s}
  #stage:hover ~ #dots,#dots:hover{opacity:1}
  .dot{width:8px;height:8px;border-radius:50%;background:#5F6368;cursor:pointer;transition:transform .15s,background .15s}
  .dot.on{background:#8AB4F8;transform:scale(1.35)}
  .dot:hover{background:#AECBFA}
  /* click zones */
  #prevZone,#nextZone{position:fixed;top:0;bottom:46px;width:18%;z-index:5;cursor:pointer}
  #prevZone{left:0}#nextZone{right:0}
  #help{position:fixed;top:14px;right:18px;color:#5F6368;font-size:12px;z-index:10;opacity:0;transition:opacity .25s}
  #stage:hover ~ #help{opacity:1}
</style>
</head>
<body>
<div id="stage"><div id="wrap"><iframe id="frame" title="slide"></iframe></div></div>
<div id="prevZone" title="Previous"></div>
<div id="nextZone" title="Next"></div>
<div id="help">← → / Space · F fullscreen</div>
<div id="dots"></div>
<div id="hud">
  <span class="nav" id="prev">‹ Prev</span>
  <span class="nav" id="next">Next ›</span>
  <span id="title"></span>
  <span id="count"></span>
</div>
<script>
const SLIDES=[
%SLIDES%
];
let i=0;
const frame=document.getElementById('frame'),
      title=document.getElementById('title'),
      count=document.getElementById('count'),
      dotsEl=document.getElementById('dots');
SLIDES.forEach((s,idx)=>{const d=document.createElement('div');d.className='dot';d.title=s.label;
  d.onclick=()=>go(idx);dotsEl.appendChild(d);});
function fit(){const s=Math.min(innerWidth/1920,(innerHeight-46)/1080);
  document.getElementById('wrap').style.transform='translate(-50%,-50%) scale('+s+')';}
function go(n){i=(n+SLIDES.length)%SLIDES.length;const s=SLIDES[i];
  frame.src=s.src;title.textContent=s.label;
  count.textContent=(i+1)+' / '+SLIDES.length+(s.badge?'   ·   '+s.badge:'');
  [...dotsEl.children].forEach((d,idx)=>d.classList.toggle('on',idx===i));}
function next(){go(i+1)}function prev(){go(i-1)}
document.getElementById('next').onclick=next;
document.getElementById('prev').onclick=prev;
document.getElementById('nextZone').onclick=next;
document.getElementById('prevZone').onclick=prev;
addEventListener('keydown',e=>{
  if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();next();}
  else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();prev();}
  else if(e.key==='Home'){go(0);} else if(e.key==='End'){go(SLIDES.length-1);}
  else if(e.key==='f'||e.key==='F'){if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen();}
});
addEventListener('resize',fit);
fit();go(0);
</script>
</body>
</html>
"""

doc = doc.replace("%SLIDES%", js_slides)
open(OUT, "w", encoding="utf-8").write(doc)
size_kb = os.path.getsize(OUT) // 1024
print(f"\nwrote {OUT}  ({size_kb} KB, self-contained)")
