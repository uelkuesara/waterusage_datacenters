"""Visual identity: black + teal "data center blueprint" look, ambient particle wave,
and the terminal-style opening sequence.

Streamlit renders st.html scripts in the main document, so the intro and the
background canvas are attached straight to <body> (outside Streamlit's React tree)
and survive reruns.

Intro timeline (approx.):
    0.0-1.0   boot log lines
    1.1-4.8   quote typed in a mono font, then the attribution
    5.9-7.3   glitch: RGB split, scrambled glyphs, error messages
    7.3-7.9   CRT switch-off collapse, revealing the app
"""

from __future__ import annotations

import base64
import json

import streamlit as st

QUOTE = "When the last tree has fallen and all the rivers are poisoned, you cannot eat money."
AUTHOR = "AURORA"

TEAL = "#4fe3c1"

# Faint blueprint tile: racks, cages and cooling units drawn as thin lines.
_TILE = (
    "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' fill='none' "
    "stroke='%234fe3c1' stroke-opacity='0.10' stroke-width='1'>"
    "<rect x='12' y='12' width='70' height='52'/><rect x='20' y='20' width='54' height='36'/>"
    "<path d='M20 38h54M47 20v36'/>"
    "<path d='M150 14l18 0 13 13 0 18-13 13-18 0-13-13 0-18z'/><path d='M155 26l8 0 6 6 0 8-6 6-8 0-6-6 0-8z'/>"
    "<rect x='104' y='80' width='26' height='70'/><rect x='134' y='80' width='26' height='70'/>"
    "<rect x='164' y='80' width='26' height='70'/><path d='M104 96h86M104 112h86M104 128h86'/>"
    "<rect x='14' y='100' width='64' height='64'/><circle cx='46' cy='132' r='20'/><circle cx='46' cy='132' r='6'/>"
    "<path d='M20 190h40v34H20zM66 190h22v34H66zM100 196h120M100 208h90M100 220h110'/>"
    "<path d='M210 120h20v80h-20z'/>"
    "</svg>"
)
_TILE_URI = "data:image/svg+xml;utf8," + _TILE.replace("#", "%23").replace("<", "%3C").replace(">", "%3E")

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&display=swap');
:root{--teal:#4fe3c1;--teal-dim:rgba(79,227,193,.55);--line:rgba(79,227,193,.18);
  --panel:rgba(6,16,18,.62);--ink:#e8fffb;--mute:#8fb5ad;--mono:'Share Tech Mono',ui-monospace,monospace;}
html{background:
  radial-gradient(ellipse 70% 60% at 60% 45%,rgba(0,0,0,.92),rgba(0,0,0,.55) 75%,rgba(0,0,0,.35)),
  url("__TILE__") 0 0/240px 240px,#000;}
body{background:transparent!important;}
.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"],[data-testid="stHeader"],
[data-testid="stBottomBlockContainer"]{background:transparent!important;}
#tc-bg{position:fixed;inset:0;width:100vw;height:100vh;z-index:-1;pointer-events:none;}

/* header: keep the toolbar (it holds the "open sidebar" button), hide the rest */
[data-testid="stDecoration"],[data-testid="stAppDeployButton"],[data-testid="stMainMenu"],
[data-testid="stToolbarActions"]{display:none!important;}
[data-testid="stExpandSidebarButton"]{background:rgba(6,20,22,.7);border:1px solid var(--teal-dim);border-radius:12px;
  backdrop-filter:blur(12px);box-shadow:0 0 0 0 rgba(79,227,193,.6);animation:tc-beacon 2.4s ease-out infinite;
  margin:6px 0 0 6px;}
[data-testid="stExpandSidebarButton"] *{color:var(--teal)!important;}
[data-testid="stExpandSidebarButton"]:hover{background:rgba(79,227,193,.15);}
@keyframes tc-beacon{0%{box-shadow:0 0 0 0 rgba(79,227,193,.55)}80%,100%{box-shadow:0 0 0 14px rgba(79,227,193,0)}}

/* ---------- liquid glass sidebar ---------- */
section[data-testid="stSidebar"]{background:transparent!important;border:none!important;padding:16px 0 16px 16px;}
section[data-testid="stSidebar"]>div:first-child{background:transparent;}
[data-testid="stSidebarContent"]{position:relative;height:calc(100vh - 32px);border-radius:24px;overflow:hidden;
  background:linear-gradient(165deg,rgba(79,227,193,.16) 0%,rgba(255,255,255,.05) 28%,rgba(255,255,255,.02) 60%,rgba(0,0,0,.35) 100%);
  backdrop-filter:blur(26px) saturate(160%);-webkit-backdrop-filter:blur(26px) saturate(160%);
  border:1px solid rgba(79,227,193,.22);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.28),inset 1px 0 0 rgba(255,255,255,.06),0 24px 60px -10px rgba(0,0,0,.8),
    0 0 40px -18px rgba(79,227,193,.5);}
[data-testid="stSidebarContent"]::after{content:"";position:absolute;inset:0;pointer-events:none;border-radius:24px;
  background:radial-gradient(120% 35% at 0% 0%,rgba(255,255,255,.12),transparent 60%);}
[data-testid="stSidebarHeader"]{position:relative;padding:1.6rem 1.4rem 1.2rem;margin-bottom:.4rem;
  border-bottom:1px solid var(--line);}
[data-testid="stSidebarHeader"]::before{content:"THIRSTY_COMPUTE";white-space:nowrap;font-family:var(--mono);font-size:1.15rem;letter-spacing:.06em;
  color:var(--ink);letter-spacing:.01em;text-shadow:0 0 18px rgba(79,227,193,.55);}
[data-testid="stSidebarNav"]::before{content:"// MENU";display:block;padding:.4rem 1.4rem .6rem;
  font:500 .7rem var(--mono);letter-spacing:.22em;color:var(--teal-dim);}
[data-testid="stSidebarNavItems"]{padding:0 .7rem;}
a[data-testid="stSidebarNavLink"]{border-radius:14px;padding:.65rem .8rem;margin:.15rem 0;transition:background .2s,box-shadow .2s,transform .2s;}
a[data-testid="stSidebarNavLink"] span{color:rgba(232,255,251,.8)!important;font-weight:400;}
a[data-testid="stSidebarNavLink"]:hover{background:rgba(79,227,193,.08);transform:translateX(3px);}
a[data-testid="stSidebarNavLink"][aria-current="page"]{background:rgba(79,227,193,.12);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.18),0 0 0 1px rgba(79,227,193,.25),0 6px 24px -8px rgba(79,227,193,.6);}
a[data-testid="stSidebarNavLink"][aria-current="page"] span{color:#fff!important;font-weight:500;}

/* ---------- content ---------- */
.block-container{padding-top:3.5rem;max-width:1200px;}
h1{font-family:var(--mono)!important;font-size:3.3rem!important;font-weight:400!important;line-height:1.08!important;color:var(--ink)!important;
  text-shadow:0 0 28px rgba(79,227,193,.35);animation:tc-title 1.1s cubic-bezier(.2,.7,.2,1) both;}
@keyframes tc-title{from{opacity:0;letter-spacing:.25em;filter:blur(8px)}to{opacity:1;letter-spacing:-.01em;filter:none}}
h2,h3,h4{font-family:var(--mono)!important;font-weight:400!important;color:var(--ink)!important;letter-spacing:-.005em;}
h3::before,h4::before{content:"// ";font-family:var(--mono);font-size:.7em;color:var(--teal);vertical-align:.12em;}
[data-testid="stCaptionContainer"]{font-family:var(--mono);font-size:.78rem!important;color:var(--mute)!important;}
strong{color:var(--teal);font-weight:600;}
[data-testid="stMainBlockContainer"] [data-testid="stVerticalBlock"]>div{animation:tc-up .7s ease-out both;}
@keyframes tc-up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}

/* HUD metric cards with corner brackets */
[data-testid="stMetric"]{position:relative;background:var(--panel);border:1px solid var(--line);border-radius:4px;
  padding:1.1rem 1.3rem;backdrop-filter:blur(10px);transition:border-color .25s,box-shadow .25s,transform .25s;}
[data-testid="stMetric"]::before,[data-testid="stMetric"]::after{content:"";position:absolute;width:14px;height:14px;
  border:2px solid var(--teal);transition:all .3s;}
[data-testid="stMetric"]::before{top:-1px;left:-1px;border-right:none;border-bottom:none;}
[data-testid="stMetric"]::after{bottom:-1px;right:-1px;border-left:none;border-top:none;}
[data-testid="stMetric"]:hover{transform:translateY(-3px);border-color:rgba(79,227,193,.45);box-shadow:0 0 36px -10px rgba(79,227,193,.45);}
[data-testid="stMetric"]:hover::before,[data-testid="stMetric"]:hover::after{width:28px;height:28px;}
[data-testid="stMetricLabel"] p{font-family:var(--mono);font-size:.72rem!important;text-transform:uppercase;letter-spacing:.12em;color:var(--mute)!important;}
[data-testid="stMetricValue"]{font-family:var(--mono);font-weight:400;color:var(--teal);text-shadow:0 0 18px rgba(79,227,193,.45);}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:6px;border-color:var(--line)!important;background:var(--panel);backdrop-filter:blur(10px);}
a[data-testid="stPageLink-NavLink"]{border:1px solid var(--line);border-radius:4px;font-family:var(--mono);transition:all .2s;}
a[data-testid="stPageLink-NavLink"]:hover{background:rgba(79,227,193,.1);border-color:var(--teal);box-shadow:0 0 20px -6px rgba(79,227,193,.6);}
hr{border-color:var(--line)!important;}
[data-testid="stSlider"] [role="slider"]{box-shadow:0 0 12px rgba(79,227,193,.8);}
iframe{color-scheme:normal;}
</style>
""".replace("__TILE__", _TILE_URI)


_INTRO_CSS = """
#tc-intro{position:fixed;inset:0;z-index:999999;background:#000;overflow:hidden;cursor:pointer;
  font-family:'Share Tech Mono',ui-monospace,monospace;color:#e8fffb;transform-origin:50% 50%;}
#tc-intro canvas{position:absolute;inset:0;width:100%;height:100%;}
#tc-intro .scan{position:absolute;inset:0;pointer-events:none;
  background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0 1px,transparent 1px 3px);mix-blend-mode:multiply;}
#tc-intro .vig{position:absolute;inset:0;pointer-events:none;background:radial-gradient(ellipse at center,transparent 45%,rgba(0,0,0,.85));}
#tc-intro .boot{position:absolute;left:28px;top:24px;font-size:12px;line-height:1.7;color:rgba(79,227,193,.6);white-space:pre;}
#tc-intro .boot b{color:#4fe3c1;font-weight:500;}
#tc-intro .stage{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;padding:0 9vw;}
#tc-intro .box{width:min(100%,62rem);font-size:clamp(1.3rem,2.8vw,2.6rem);}
#tc-intro .q{font-weight:400;line-height:1.45;text-align:left;text-shadow:0 0 18px rgba(79,227,193,.35);min-height:4.4em;}
#tc-intro .q .pr{color:#4fe3c1;margin-right:.5em;}
#tc-intro .a{font-size:clamp(.8rem,1.1vw,1rem);
  letter-spacing:.35em;color:#4fe3c1;margin-top:1.2rem;min-height:1.4em;}
#tc-intro .caret{display:inline-block;width:.55em;height:1.05em;background:#4fe3c1;vertical-align:-.15em;margin-left:.08em;
  box-shadow:0 0 12px #4fe3c1;animation:tc-blink 1s steps(1) infinite;}
@keyframes tc-blink{50%{opacity:0}}
#tc-intro .skip{position:absolute;right:24px;bottom:20px;font-size:11px;letter-spacing:.25em;color:rgba(232,255,251,.35);}
#tc-intro .err{position:absolute;font-size:clamp(.7rem,1vw,.9rem);color:#ff3d5a;background:rgba(255,61,90,.08);
  border:1px solid rgba(255,61,90,.6);padding:.35em .7em;letter-spacing:.08em;white-space:nowrap;
  text-shadow:0 0 10px rgba(255,61,90,.8);animation:tc-errin .12s steps(2) both;}
@keyframes tc-errin{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:none}}
#tc-intro.glitch .stage{animation:tc-jit .18s steps(2) infinite;}
#tc-intro.glitch .q{animation:tc-rgb .25s steps(3) infinite,tc-slice .4s steps(4) infinite;}
@keyframes tc-jit{0%{transform:translate(0)}25%{transform:translate(-6px,2px)}50%{transform:translate(5px,-3px)}75%{transform:translate(-3px,-1px)}}
@keyframes tc-rgb{0%{text-shadow:-3px 0 #ff3d5a,3px 0 #4fe3c1}50%{text-shadow:4px 0 #ff3d5a,-4px 0 #3ab8ff}100%{text-shadow:-2px 1px #ff3d5a,2px -1px #4fe3c1}}
@keyframes tc-slice{0%{clip-path:inset(0 0 0 0)}25%{clip-path:inset(12% 0 55% 0);transform:translateX(-14px)}
  50%{clip-path:inset(48% 0 20% 0);transform:translateX(18px)}75%{clip-path:inset(70% 0 4% 0);transform:translateX(-8px)}100%{clip-path:inset(0 0 0 0)}}
#tc-intro.glitch .flash{position:absolute;inset:0;background:#4fe3c1;mix-blend-mode:overlay;animation:tc-flash .5s steps(3) infinite;pointer-events:none;}
@keyframes tc-flash{0%,100%{opacity:0}40%{opacity:.18}60%{opacity:0}80%{opacity:.08}}
#tc-intro.off{animation:tc-crt .6s cubic-bezier(.7,0,.3,1) forwards;}
@keyframes tc-crt{0%{transform:scale(1,1);filter:brightness(1)}45%{transform:scale(1,.004);filter:brightness(3)}
  100%{transform:scale(0,.004);filter:brightness(6);opacity:.6}}
@media (prefers-reduced-motion:reduce){#tc-intro{display:none}}
"""

# Shared JS: particle wave renderer (used by the intro and the ambient background).
_WAVE_JS = r"""
function tcWave(canvas, opts){
  var ctx = canvas.getContext('2d'), dpr = Math.min(window.devicePixelRatio||1, 2), W, H, P = [], alive = true;
  var N = opts.n, A = opts.alpha;
  function size(){ W = canvas.clientWidth; H = canvas.clientHeight; canvas.width = W*dpr; canvas.height = H*dpr; ctx.setTransform(dpr,0,0,dpr,0,0); }
  size(); window.addEventListener('resize', size);
  for (var i=0;i<N;i++){
    var dust = Math.random() < .35;
    P.push({t:Math.random(), o:(Math.random()-.5)*2, r:Math.random()*1.6+.3, s:.0003+Math.random()*.0009,
      a:Math.random()*.8+.2, dust:dust, x:Math.random(), y:Math.random(), ph:Math.random()*6.28});
  }
  function frame(ms){
    if (!alive) return;
    var tm = ms/1000; ctx.clearRect(0,0,W,H);
    for (var i=0;i<N;i++){
      var p = P[i], x, y, a;
      if (p.dust){ x = p.x*W + Math.sin(tm*.2+p.ph)*8; y = ((p.y - tm*.004*p.r) % 1 + 1) % 1 * H; a = .25*p.a; }
      else {
        p.t += p.s; if (p.t > 1.1) p.t = -.1;
        var t = p.t, spread = (.25 + Math.pow(Math.abs(t-.5)*2, 1.5)) * H * .09;
        x = t*W;
        y = H*opts.y + Math.sin(t*6.283*1.1 + tm*.5)*H*.11 + Math.sin(t*15 + tm*.9)*H*.025 + p.o*spread*(.6+.4*Math.sin(tm+p.ph));
        a = p.a * (1 - Math.abs(p.o)*.6);
      }
      ctx.globalAlpha = a*A; ctx.fillStyle = '#4fe3c1';
      ctx.beginPath(); ctx.arc(x, y, p.r, 0, 6.283); ctx.fill();
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
  return function(){ alive = false; };
}
"""


def _intro_js(boot_lines: list[str]) -> str:
    return r"""
(function(){
  var played = false;
  // once per full page load: Streamlit reruns and in-app page switches keep `window`, a reload doesn't
  played = !!window.__tcIntroPlayed; window.__tcIntroPlayed = true;
  if (played || document.getElementById('tc-intro')) return;
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var QUOTE = __QUOTE__, AUTHOR = __AUTHOR__, BOOT = __BOOT__;
  var st = document.createElement('style'); st.textContent = __CSS__; document.head.appendChild(st);
  var el = document.createElement('div'); el.id = 'tc-intro';
  el.innerHTML = '<canvas></canvas><div class="boot"></div><div class="stage"><div class="box"><div class="q"></div><div class="a"></div></div></div>'
    + '<div class="flash"></div><div class="scan"></div><div class="vig"></div><div class="skip">CLICK TO SKIP</div>';
  document.body.appendChild(el);
  var stopWave = tcWave(el.querySelector('canvas'), {n: 1400, alpha: 1, y: .5});
  var q = el.querySelector('.q'), a = el.querySelector('.a'), boot = el.querySelector('.boot');
  var caret = '<span class="caret"></span>', timers = [], finished = false;
  function later(fn, ms){ timers.push(setTimeout(fn, ms)); }
  function esc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;'); }

  // 1. boot log
  BOOT.forEach(function(line, i){ later(function(){ boot.innerHTML += line + '\n'; }, 120 + i*220); });

  // 2. type the quote
  var t = 1100, i;
  for (i = 1; i <= QUOTE.length; i++) (function(n){
    later(function(){ q.innerHTML = '<span class="pr">&gt;</span>' + esc(QUOTE.slice(0,n)) + caret; }, t);
    var ch = QUOTE[n-1]; t += (ch === ',' ? 260 : ch === ' ' ? 55 : 32) + Math.random()*22;
  })(i);
  t += 250;
  for (i = 0; i <= AUTHOR.length + 3; i++) (function(n){
    later(function(){ a.textContent = ('// ' + AUTHOR).slice(0, n); }, t);
    t += 60;
  })(i);

  // 3. error / glitch
  var GLYPHS = '█▓▒░<>/\\|#$%&01{}[]_=+*';
  var ERRS = ['ERR 0x57A7 :: COOLING_WATER_EXHAUSTED', 'FATAL :: aquifer.read() -> EOF', 'SEGFAULT @ 0x00000H2O',
              'WARN :: basin_stress > 0.80', 'KERNEL PANIC :: river.status = POISONED', 'E_CANNOT_EAT :: money'];
  var gStart = t + 1100;
  later(function(){ el.classList.add('glitch'); }, gStart);
  for (i = 0; i < 14; i++) (function(k){
    later(function(){
      var s = QUOTE.split(''), frac = (k+1)/14;
      for (var j=0;j<s.length;j++) if (s[j] !== ' ' && Math.random() < frac) s[j] = GLYPHS[Math.floor(Math.random()*GLYPHS.length)];
      q.innerHTML = '<span class="pr">&gt;</span>' + esc(s.join(''));
      if (k % 2 === 0){
        var e = document.createElement('div'); e.className = 'err'; e.textContent = ERRS[(k/2)%ERRS.length];
        e.style.left = (6 + Math.random()*60) + '%'; e.style.top = (8 + Math.random()*80) + '%';
        el.appendChild(e);
      }
    }, gStart + k*95);
  })(i);

  // 4. CRT switch-off
  function finish(){
    if (finished) return; finished = true; timers.forEach(clearTimeout);
    el.classList.add('glitch'); el.classList.add('off');
    setTimeout(function(){ stopWave(); el.remove(); st.remove(); }, 650);
  }
  later(finish, gStart + 14*95 + 150);
  el.addEventListener('click', finish);
})();
""".replace("__QUOTE__", json.dumps(QUOTE)).replace("__AUTHOR__", json.dumps(AUTHOR)) \
   .replace("__BOOT__", json.dumps(boot_lines)).replace("__CSS__", json.dumps(_INTRO_CSS))


_BG_JS = r"""
(function(){
  if (document.getElementById('tc-bg')) return;
  var c = document.createElement('canvas'); c.id = 'tc-bg';
  document.body.insertBefore(c, document.body.firstChild);
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  tcWave(c, {n: 650, alpha: .35, y: .62});
})();
"""


def _script(js: str) -> str:
    # Streamlit's sanitizer drops <script> blocks whose text looks like HTML ("<b", "<N"...),
    # so ship the code base64-encoded and decode it (UTF-8 safe) in the browser.
    b64 = base64.b64encode(js.encode("utf-8")).decode("ascii")
    return ("<script>new Function(new TextDecoder().decode(Uint8Array.from(atob('" + b64
            + "'), function(c){ return c.charCodeAt(0); })))();</script>")


def apply(n_datacenters: int | None = None, n_states: int | None = None) -> None:
    st.html(GLOBAL_CSS)
    boot = [
        "<b>[ ok ]</b> init thirsty_compute",
        f"<b>[ ok ]</b> mount /us/datacenters ........ {n_datacenters:,} nodes" if n_datacenters
        else "<b>[ ok ]</b> mount /us/datacenters",
        f"<b>[ ok ]</b> link wri.aqueduct basins ..... {n_states} states" if n_states
        else "<b>[ ok ]</b> link wri.aqueduct basins",
        "<b>[ .. ]</b> cooling_loop.status ......... DRAWING",
    ]
    st.html(_script(_WAVE_JS + _BG_JS + _intro_js(boot)), unsafe_allow_javascript=True)
