"""Animated water-risk map (D3 in a Streamlit component iframe).

Why not Plotly: plotly geo grabs the scroll wheel, so scrolling the page zoomed the
map. Here the wheel only zooms with Ctrl/Cmd held (trackpad pinch sends ctrlKey,
so pinch still works); a plain scroll passes through to the page.

Interactions: scenario pills (animated recolor), click a state to fly to it,
+ / - / reset buttons, drag to pan when zoomed, HUD crosshair with lon/lat readout,
ambient "ping" rings on random data centers.
"""

from __future__ import annotations

import json

import pandas as pd
import streamlit.components.v1 as components

from . import ui

SCEN = {"bau": "business as usual", "opt": "optimistic", "pes": "pessimistic"}


def scenarios(summary: pd.DataFrame) -> dict[str, dict[str, str]]:
    """{"Today": {"": "bws_score"}, "2030": {"business as usual": "bws_2030_bau", ...}, ...}"""
    out: dict[str, dict[str, str]] = {"Today": {"": "bws_score"}}
    for col in sorted(c for c in summary.columns if c.startswith("bws_20")):
        _, year, scen = col.split("_")
        out.setdefault(year, {})[SCEN.get(scen, scen)] = col
    return out


def render(summary: pd.DataFrame, dcs: pd.DataFrame | None, height: int = 700) -> None:
    scen = scenarios(summary)
    states = [
        {
            "name": r.state_name, "abbr": r.state, "dc": int(r.datacenters), "label": r.bws_label,
            "s": {col: (None if pd.isna(getattr(r, col)) else round(float(getattr(r, col)), 3))
                  for opts in scen.values() for col in opts.values()},
        }
        for r in summary.itertuples()
    ]
    points = []
    if dcs is not None:
        for r in dcs.itertuples():
            points.append([round(r.lon, 3), round(r.lat, 3),
                           r.name if isinstance(r.name, str) else "Unnamed data center",
                           r.operator if isinstance(r.operator, str) else ""])
    payload = json.dumps({"states": states, "points": points, "scenarios": scen,
                          "colors": ui.STRESS_COLORS})
    components.html(_HTML.replace("__DATA__", payload.replace("<", "\\u003c")), height=height)


_HTML = r"""
<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Montserrat:wght@300;400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>
<style>
:root{--teal:#4fe3c1;--line:rgba(79,227,193,.2);--ink:#e8fffb;--mute:#8fb5ad;--mono:'Share Tech Mono',monospace;}
*{box-sizing:border-box}
html,body{margin:0;background:transparent;color:var(--ink);font-family:Montserrat,sans-serif;overflow:hidden;}
#wrap{position:relative;height:100vh;background-color:rgba(0,4,5,.82)!important;border:1px solid var(--line);border-radius:6px;overflow:hidden;
  background:radial-gradient(ellipse at 50% 55%,rgba(79,227,193,.07),rgba(0,0,0,.55) 70%);}
#wrap::before{content:"";position:absolute;inset:0;pointer-events:none;
  background-image:linear-gradient(rgba(79,227,193,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(79,227,193,.05) 1px,transparent 1px);
  background-size:40px 40px;}
.corner{position:absolute;width:18px;height:18px;border:2px solid var(--teal);pointer-events:none;z-index:5}
.c1{top:6px;left:6px;border-right:0;border-bottom:0}.c2{top:6px;right:6px;border-left:0;border-bottom:0}
.c3{bottom:6px;left:6px;border-right:0;border-top:0}.c4{bottom:6px;right:6px;border-left:0;border-top:0}
#bar{position:absolute;top:14px;left:18px;right:18px;display:flex;gap:10px;align-items:center;flex-wrap:wrap;z-index:6}
.pill{font:400 11px var(--mono);letter-spacing:.06em;color:var(--mute);background:rgba(0,0,0,.45);border:1px solid var(--line);
  padding:6px 10px;border-radius:3px;cursor:pointer;transition:all .2s;text-transform:uppercase}
.pill:hover{color:var(--ink);border-color:var(--teal)}
.pill.on{color:#001512;background:var(--teal);border-color:var(--teal);box-shadow:0 0 18px rgba(79,227,193,.55)}
#yearSel,#scenSel{display:flex;gap:6px}.sep{width:1px;height:20px;background:var(--line)}
.pill.off{opacity:.3;pointer-events:none}
#zoom{position:absolute;right:18px;top:64px;display:flex;flex-direction:column;gap:6px;z-index:6}
#zoom button{width:34px;height:34px;font:400 16px var(--mono);color:var(--teal);background:rgba(0,0,0,.55);
  border:1px solid var(--line);border-radius:3px;cursor:pointer;transition:all .2s}
#zoom button:hover{border-color:var(--teal);box-shadow:0 0 14px rgba(79,227,193,.5)}
svg{position:absolute;left:0;right:0;top:56px;bottom:30px;width:100%;height:calc(100% - 86px);cursor:crosshair}
.state{stroke:rgba(79,227,193,.35);stroke-width:.6;transition:opacity .5s}
.state:hover{stroke:#fff;stroke-width:1.4}
.state.sel{stroke:var(--teal);stroke-width:2;filter:url(#glow)}
.dim .state:not(.sel){opacity:.28}
.dot{fill:#e8fffb;pointer-events:all}
.dot:hover{fill:var(--teal)}
.ping{fill:none;stroke:var(--teal);pointer-events:none}
.lbl{font:500 9px var(--mono);fill:#e8fffb;text-anchor:middle;pointer-events:none;letter-spacing:.08em;paint-order:stroke;stroke:#000;stroke-width:2px}
#scan{position:absolute;top:0;bottom:0;width:2px;background:var(--teal);box-shadow:0 0 24px 6px rgba(79,227,193,.6);left:-10px;pointer-events:none;z-index:4}
#xh-h,#xh-v{position:absolute;background:rgba(79,227,193,.25);pointer-events:none;display:none;z-index:3}
#xh-h{left:0;right:0;height:1px}#xh-v{top:0;bottom:0;width:1px}
#hud{position:absolute;right:18px;bottom:16px;font:400 10px var(--mono);color:var(--mute);text-align:right;line-height:1.7;letter-spacing:.08em;z-index:6}
#hud b{color:var(--teal);font-weight:500}
#legend{position:absolute;left:18px;bottom:16px;z-index:6;font:400 10px var(--mono);color:var(--mute);letter-spacing:.08em}
#legend .grad{width:220px;height:8px;border-radius:2px;margin:6px 0 4px;border:1px solid var(--line)}
#legend .ticks{display:flex;justify-content:space-between;width:220px}
#tip{position:absolute;pointer-events:none;z-index:9;font:400 11px var(--mono);background:rgba(4,14,16,.92);border:1px solid var(--teal);
  padding:8px 10px;border-radius:3px;opacity:0;transition:opacity .15s;max-width:260px;line-height:1.55;box-shadow:0 0 20px rgba(79,227,193,.3)}
#tip b{color:var(--teal);font-weight:500}
#card{position:absolute;left:18px;top:64px;width:250px;z-index:6;background:rgba(4,14,16,.82);border:1px solid var(--line);
  backdrop-filter:blur(8px);padding:14px 16px;border-radius:4px;transform:translateX(-120%);transition:transform .6s cubic-bezier(.2,.8,.2,1)}
#card.on{transform:none}
#card .k{font:400 10px var(--mono);color:var(--mute);letter-spacing:.14em;text-transform:uppercase;margin-top:10px}
#card .v{font:400 28px var(--mono);color:var(--teal);text-shadow:0 0 14px rgba(79,227,193,.5)}
#card .n{font:400 22px var(--mono);color:var(--ink)}
#card .x{position:absolute;top:8px;right:10px;cursor:pointer;color:var(--mute);font:400 14px var(--mono)}
#card .meter{height:4px;background:rgba(255,255,255,.08);margin-top:6px;border-radius:2px;overflow:hidden}
#card .meter i{display:block;height:100%;width:0;transition:width .9s cubic-bezier(.2,.8,.2,1)}
#hint{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);z-index:8;font:400 12px var(--mono);letter-spacing:.12em;
  background:rgba(0,0,0,.75);border:1px solid var(--teal);padding:10px 16px;border-radius:3px;opacity:0;transition:opacity .3s;pointer-events:none}
</style></head><body>
<div id="wrap">
  <div class="corner c1"></div><div class="corner c2"></div><div class="corner c3"></div><div class="corner c4"></div>
  <div id="bar"><span class="pill on" id="ptsBtn">● Data centers</span><span class="sep"></span><div id="yearSel"></div><span class="sep"></span><div id="scenSel"></div></div>
  <div id="zoom"><button id="zin" title="Zoom in">+</button><button id="zout" title="Zoom out">&minus;</button><button id="zreset" title="Reset">&#8634;</button></div>
  <svg id="map" viewBox="0 0 975 610" preserveAspectRatio="xMidYMid meet">
    <defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
    <g id="zoomg"><g id="states"></g><g id="labels"></g><g id="pings"></g><g id="dots"></g></g>
  </svg>
  <div id="scan"></div><div id="xh-h"></div><div id="xh-v"></div>
  <div id="card"><span class="x" id="cx">✕</span><div class="n" id="cn"></div>
    <div class="k">Water stress <span id="cs"></span></div><div class="v" id="cv">0.00</div><div class="meter"><i id="cm"></i></div>
    <div class="k">Category</div><div style="font:400 12px var(--mono);margin-top:4px" id="cl"></div>
    <div class="k">Mapped data centers</div><div class="v" id="cd">0</div></div>
  <div id="legend">WATER STRESS (0–5)<div class="grad"></div><div class="ticks"><span>0</span><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span></div></div>
  <div id="hud"></div>
  <div id="tip"></div>
  <div id="hint">HOLD ⌘ / CTRL + SCROLL TO ZOOM · OR PINCH</div>
</div>
<script>
const D = __DATA__;
const colors = D.colors;
const color = d3.scaleLinear().domain([0,1,2,3,4,5]).range(colors).clamp(true);
document.querySelector('#legend .grad').style.background = 'linear-gradient(90deg,' + colors.join(',') + ')';
const byName = new Map(D.states.map(s => [s.name, s]));
let scenCol = 'bws_score', scenLabel = 'Today', showPts = true, k = 1, selected = null;
const projection = d3.geoAlbersUsa().scale(1300).translate([487.5, 305]);
const svg = d3.select('#map'), g = d3.select('#zoomg');
const tip = document.getElementById('tip'), hud = document.getElementById('hud');

// scenario pills: horizon (Today / 2030 / 2050 / 2080) x pathway
const S = D.scenarios;  // {"Today": {"": col}, "2030": {"optimistic": col, ...}}
let year = 'Today', path = 'business as usual';
const ys = document.getElementById('yearSel'), ps = document.getElementById('scenSel');
const pathways = [...new Set(Object.values(S).flatMap(o => Object.keys(o)).filter(Boolean))];
function pick() {
  const o = S[year]; const p = o[path] !== undefined ? path : Object.keys(o)[0];
  scenCol = o[p]; scenLabel = year === 'Today' ? 'Today' : `${year} · ${p}`;
  ys.querySelectorAll('.pill').forEach(b => b.classList.toggle('on', b.dataset.v === year));
  ps.querySelectorAll('.pill').forEach(b => { b.classList.toggle('on', year !== 'Today' && b.dataset.v === path); b.classList.toggle('off', year === 'Today'); });
  if (window._recolor) window._recolor(true);
}
Object.keys(S).sort((a, b) => a === 'Today' ? -1 : b === 'Today' ? 1 : a.localeCompare(b)).forEach(y => { const b = document.createElement('span'); b.className = 'pill'; b.textContent = y; b.dataset.v = y;
  b.onclick = () => { year = y; pick(); }; ys.appendChild(b); });
pathways.forEach(p => { const b = document.createElement('span'); b.className = 'pill'; b.dataset.v = p;
  b.textContent = {'business as usual': 'BAU', 'optimistic': 'Optimistic', 'pessimistic': 'Pessimistic'}[p] || p;
  b.title = p; b.onclick = () => { path = p; pick(); }; ps.appendChild(b); });
pick();

d3.json('https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-albers-10m.json').then(us => {
  const path = d3.geoPath();
  const feats = topojson.feature(us, us.objects.states).features;
  const statesSel = d3.select('#states').selectAll('path').data(feats).join('path')
    .attr('class', 'state').attr('d', path).attr('fill', '#05100f')
    .on('mousemove', (ev, f) => { const s = byName.get(f.properties.name); showTip(ev,
        `<b>${f.properties.name}</b><br>stress ${val(s) == null ? 'n/a' : val(s).toFixed(2)} · ${scenLabel}<br>${s ? s.dc : 0} data centers`); })
    .on('mouseleave', hideTip)
    .on('click', (ev, f) => { ev.stopPropagation(); focusState(f, path); });

  // intro: a scan line sweeps left to right and states light up as it passes
  const cx = f => path.centroid(f)[0] || 0;
  statesSel.transition().delay(f => 200 + cx(f) * 1.4).duration(700)
    .attr('fill', f => fillFor(f));
  d3.select('#scan').transition().duration(1600).ease(d3.easeCubicInOut).styleTween('left', () => t => (t * 102 - 1) + '%')
    .transition().duration(300).style('opacity', 0);

  // state labels (fade in when zoomed)
  d3.select('#labels').selectAll('text').data(feats).join('text').attr('class', 'lbl')
    .attr('x', f => path.centroid(f)[0]).attr('y', f => path.centroid(f)[1])
    .text(f => (byName.get(f.properties.name) || {}).abbr || '').style('opacity', 0);

  // data center dots pop in, west to east
  const pts = D.points.map(p => { const xy = projection([p[0], p[1]]); return xy ? {x: xy[0], y: xy[1], name: p[2], op: p[3], lon: p[0], lat: p[1]} : null; }).filter(Boolean);
  const dots = d3.select('#dots').selectAll('circle').data(pts).join('circle').attr('class', 'dot')
    .attr('cx', d => d.x).attr('cy', d => d.y).attr('r', 0).style('opacity', .9)
    .on('mousemove', (ev, d) => showTip(ev, `<b>${esc(d.name)}</b>${d.op ? '<br>' + esc(d.op) : ''}<br>${d.lat.toFixed(2)}°, ${d.lon.toFixed(2)}°`))
    .on('mouseleave', hideTip);
  dots.transition().delay(d => 900 + d.x * 1.2 + Math.random() * 200).duration(500).ease(d3.easeBackOut.overshoot(3))
    .attr('r', rDot);

  // ambient pings on random data centers
  setInterval(() => {
    if (!showPts || !pts.length) return;
    const d = pts[Math.floor(Math.random() * pts.length)];
    d3.select('#pings').append('circle').attr('class', 'ping').attr('cx', d.x).attr('cy', d.y)
      .attr('r', 1 / k).attr('stroke-width', 1.2 / k).style('opacity', 1)
      .transition().duration(1600).ease(d3.easeCubicOut).attr('r', 18 / k).style('opacity', 0).remove();
  }, 140);

  document.getElementById('ptsBtn').onclick = (e) => {
    showPts = !showPts; e.target.classList.toggle('on', showPts);
    dots.transition().duration(500).delay(d => showPts ? d.x * .6 : (975 - d.x) * .4).attr('r', showPts ? rDot() : 0);
  };

  function fillFor(f) { const s = byName.get(f.properties.name); const v = val(s); return v == null ? '#0a0f10' : color(v); }
  function recolor(sweep) {
    statesSel.transition().delay(f => sweep ? cx(f) * .8 : 0).duration(800).attr('fill', fillFor);
    if (selected) fillCard(selected);
  }
  window._recolor = recolor;

  // ---- zoom ----
  const zoom = d3.zoom().scaleExtent([1, 10]).translateExtent([[-100, -100], [1075, 710]])
    .filter(ev => ev.type === 'wheel' ? (ev.ctrlKey || ev.metaKey) : (!ev.button && ev.type !== 'dblclick'))
    .on('zoom', ev => {
      k = ev.transform.k; g.attr('transform', ev.transform);
      dots.attr('r', showPts ? rDot() : 0);
      d3.selectAll('.state').style('stroke-width', (selected ? null : .6 / k));
      d3.selectAll('.lbl').style('opacity', Math.max(0, Math.min(1, (k - 1.8) / 1.2))).style('font-size', (9 / Math.sqrt(k)) + 'px');
      hudUpdate();
    });
  svg.call(zoom);
  let hintT;
  svg.node().addEventListener('wheel', ev => { if (!(ev.ctrlKey || ev.metaKey)) { const h = document.getElementById('hint'); h.style.opacity = 1; clearTimeout(hintT); hintT = setTimeout(() => h.style.opacity = 0, 1100); } }, {passive: true});
  const T = 850;
  document.getElementById('zin').onclick = () => svg.transition().duration(T).ease(d3.easeCubicInOut).call(zoom.scaleBy, 1.8);
  document.getElementById('zout').onclick = () => svg.transition().duration(T).ease(d3.easeCubicInOut).call(zoom.scaleBy, 1 / 1.8);
  const reset = () => { selected = null; d3.select('#wrap').classed('dim', false); statesSel.classed('sel', false);
    document.getElementById('card').classList.remove('on');
    svg.transition().duration(1100).ease(d3.easeCubicInOut).call(zoom.transform, d3.zoomIdentity); };
  document.getElementById('zreset').onclick = reset; document.getElementById('cx').onclick = reset;
  svg.on('click', () => { if (selected) reset(); });

  function focusState(f, path) {
    const [[x0, y0], [x1, y1]] = path.bounds(f);
    const s = Math.min(8, .85 / Math.max((x1 - x0) / 975, (y1 - y0) / 610));
    const t = d3.zoomIdentity.translate(975 / 2, 610 / 2).scale(s).translate(-(x0 + x1) / 2, -(y0 + y1) / 2);
    selected = f; statesSel.classed('sel', d => d === f); d3.select('#wrap').classed('dim', true);
    // zoom out a little first, then dive in: a "fly-to" arc
    svg.transition().duration(450).ease(d3.easeCubicOut).call(zoom.scaleTo, Math.max(1, k * .8))
      .transition().duration(1100).ease(d3.easeCubicInOut).call(zoom.transform, t);
    fillCard(f);
  }
  function fillCard(f) {
    const s = byName.get(f.properties.name), v = val(s);
    document.getElementById('cn').textContent = f.properties.name;
    document.getElementById('cs').textContent = '· ' + scenLabel;
    document.getElementById('cl').textContent = s ? s.label : 'n/a';
    countUp('cv', v || 0, 2); countUp('cd', s ? s.dc : 0, 0);
    const m = document.getElementById('cm'); m.style.background = color(v || 0); m.style.width = ((v || 0) / 5 * 100) + '%';
    document.getElementById('card').classList.add('on');
  }
});

function rDot() { return 1.8 / Math.pow(k, .7); }
function val(s) { return s ? s.s[scenCol] : null; }
function countUp(id, to, dec) {
  const el = document.getElementById(id), from = parseFloat(el.textContent) || 0;
  d3.select(el).transition().duration(900).ease(d3.easeCubicOut)
    .tween('t', () => { const i = d3.interpolateNumber(from, to); return t => el.textContent = i(t).toFixed(dec); });
}
function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;'); }
function showTip(ev, html) { tip.innerHTML = html; tip.style.opacity = 1;
  const r = document.getElementById('wrap').getBoundingClientRect();
  tip.style.left = Math.min(ev.clientX - r.left + 14, r.width - 270) + 'px'; tip.style.top = (ev.clientY - r.top + 14) + 'px'; }
function hideTip() { tip.style.opacity = 0; }

// HUD crosshair + readout
const xh = document.getElementById('xh-h'), xv = document.getElementById('xh-v');
let lastLL = null;
svg.on('mousemove.hud', ev => {
  const r = document.getElementById('wrap').getBoundingClientRect();
  xh.style.display = xv.style.display = 'block';
  xh.style.top = (ev.clientY - r.top) + 'px'; xv.style.left = (ev.clientX - r.left) + 'px';
  const t = d3.zoomTransform(svg.node()), p = d3.pointer(ev, svg.node());
  lastLL = projection.invert(t.invert(p)); hudUpdate();
}).on('mouseleave.hud', () => { xh.style.display = xv.style.display = 'none'; lastLL = null; hudUpdate(); });
function hudUpdate() {
  hud.innerHTML = (lastLL ? `LAT <b>${lastLL[1].toFixed(3)}</b> · LON <b>${lastLL[0].toFixed(3)}</b><br>` : '') +
    `ZOOM <b>${k.toFixed(2)}×</b> · ${D.points.length.toLocaleString()} NODES`;
}
hudUpdate();
</script></body></html>
"""
