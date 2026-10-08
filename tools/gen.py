# -*- coding: utf-8 -*-
"""Generate index.html.

Chart geometry and the icon sprite are built here so the markup can never
drift from the data in this file. Run: python3 tools/gen.py
"""
import math, os, re, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ── Data ────────────────────────────────────────────────────────────────────
# (label, tasks, css colour var, icon id)
LANGS = [
    ("Go",   818, "var(--c-go)",   "go",   "i-go"),
    ("C++",  378, "var(--c-cpp)",  "cplusplus", "i-cpp"),
    ("Rust", 303, "var(--c-rust)", "rust", "i-rust"),
    ("C",    149, "var(--c-c)",    "c",    "i-c"),
]
TOTAL = sum(v for _, v, _, _, _ in LANGS)

# (short name, variant, full name, score, is_ours, icon id or None for mascot)
MODELS = [
    ("Opus 4.8",    "xhigh",         "Claude Opus 4.8 (xhigh)",              70.90, False, "anthropic"),
    ("GPT-5.6",     "xhigh",         "GPT-5.6 Sol (xhigh)",                  69.90, False, "openai"),
    ("GLM-5.2",     "",              "GLM-5.2",                              64.60, False, "glm"),
    ("Gemini 3.7",  "Flash",         "Gemini 3.7 Flash",                     61.20, False, "google"),
    ("DS-V4",       "Flash-0731",    "DeepSeek-V4-Flash-0731",               57.68, False, "deepseek"),
    ("Qwen3.8-SFT", "Program-Agent", "Qwen3.8-27B-SFT + Program-Agent",      56.25, True,  None),
    ("Qwen3.8-27B", "Program-Agent", "Qwen3.8-27B + Program-Agent",          55.71, True,  None),
    ("Gemini 3.6",  "Flash",         "Gemini 3.6 Flash",                     55.70, False, "google"),
    ("Kimi K2.7",   "Code",          "Kimi K2.7 Code",                       53.60, False, "kimi"),
    ("Qwen3.8-SFT", "Claude Code",   "Qwen3.8-27B-SFT + Claude Code",        42.84, True,  None),
    ("Qwen3.8-27B", "",              "Qwen3.8-27B",                          34.87, False, "qwen"),
]
Y_MAX = 80.0

# Jump curves: (source bar index, target bar index). Each lands on an "ours" bar.
ARCS = [(10, 6), (9, 5)]

ICON_CLASS = {
    "anthropic": "i-anthropic", "openai": "i-openai", "glm": "i-glm",
    "google": "i-google", "deepseek": "i-deepseek", "qwen": "i-qwen",
    "kimi": "i-kimi", "go": "i-go", "cplusplus": "i-cpp", "rust": "i-rust", "c": "i-c",
}

# ── Icon sprite ─────────────────────────────────────────────────────────────
def sprite():
    """Fold the vendored simple-icons SVGs into one inline <symbol> sprite."""
    out = []
    for name in sorted(os.listdir(os.path.join(ROOT, 'tools', 'icons'))):
        if not name.endswith('.svg'):
            continue
        key = name[:-4]
        raw = open(os.path.join(ROOT, 'tools', 'icons', name), encoding='utf-8').read()
        paths = ''.join(re.findall(r'<path[^>]*/>', raw))
        vb = re.search(r'viewBox="([^"]+)"', raw).group(1)
        out.append(f'  <symbol id="ic-{key}" viewBox="{vb}">{paths}</symbol>')
    return '\n'.join(out)

def icon_svg(key, cls_extra=""):
    return (f'<svg class="mi" aria-hidden="true"><use href="#ic-{key}"></use></svg>')

# ── Donut ───────────────────────────────────────────────────────────────────
R, CIRC, GAP = 80.0, 2 * math.pi * 80.0, 2.0
CX = CY = 130.0
R_ICON = 106.0   # icon ring sits just outside the band
ICON_PX = 26.0

segs, ringicons, legend, cum = [], [], [], 0.0
for i, (name, val, col, ikey, icls) in enumerate(LANGS):
    frac = val / TOTAL
    ln = frac * CIRC
    rot = -90 + cum * 360
    delay = round(0.08 + i * 0.13, 3)
    segs.append(
        f'          <circle class="seg" r="{R:g}" cx="{CX:g}" cy="{CY:g}"\n'
        f'                  stroke="{col}"\n'
        f'                  stroke-dasharray="{ln - GAP:.3f} {CIRC - ln + GAP:.3f}"\n'
        f'                  style="--len:{ln:.3f}; --d:{delay}s"\n'
        f'                  transform="rotate({rot:.4f} {CX:g} {CY:g})"\n'
        f'                  data-name="{name}" data-count="{val}" data-pct="{frac*100:.2f}"></circle>'
    )
    # Icon at the segment's mid-angle, on a ring outside the band.
    mid = math.radians(-90 + (cum + frac / 2) * 360)
    ix = CX + R_ICON * math.cos(mid) - ICON_PX / 2
    iy = CY + R_ICON * math.sin(mid) - ICON_PX / 2
    ringicons.append(
        f'          <svg class="ringicon {icls}" x="{ix:.2f}" y="{iy:.2f}" '
        f'width="{ICON_PX:g}" height="{ICON_PX:g}" viewBox="0 0 24 24" '
        f'style="--d:{delay}s"><use href="#ic-{ikey}"></use></svg>'
    )
    legend.append(
        f'            <li style="--c:{col}" data-name="{name}">\n'
        f'              <span class="ic sw {icls}">{icon_svg(ikey)}</span>\n'
        f'              <span class="nm">{name}</span>\n'
        f'              <span class="ct">{val:,}</span>\n'
        f'              <span class="pc">{frac*100:.2f}%</span>\n'
        f'            </li>'
    )
    cum += frac

# ── Bars ────────────────────────────────────────────────────────────────────
bhead, bars = [], []
for i, (short, var, full, score, ours, ikey) in enumerate(MODELS):
    h = score / Y_MAX * 100
    mark = (f'<span class="ic"><img src="static/images/favicon.png" alt=""></span>'
            if ikey is None else
            f'<span class="ic {ICON_CLASS[ikey]}">{icon_svg(ikey)}</span>')
    bhead.append(
        f'            <div class="bh{" ours" if ours else ""}">{mark}'
        f'<span class="nm">{short}</span>'
        f'<span class="vr">{var or "&nbsp;"}</span></div>'
    )
    bars.append(
        f'            <div class="bar{" ours" if ours else ""}" style="--h:{h:.3f}%"\n'
        f'                 data-idx="{i}" data-name="{full}" data-score="{score:g}"'
        f'{" data-ours=\"1\"" if ours else ""}>\n'
        f'              <span class="bval">{score:g}</span>\n'
        f'              <i class="bfill"></i>\n'
        f'            </div>'
    )

grid = [f'            <div class="gridline" style="bottom:{t/Y_MAX*100:.2f}%"><span>{t}</span></div>'
        for t in range(0, int(Y_MAX) + 1, 20)]

# ── Pipeline diagram ────────────────────────────────────────────────────────
# Laid out on a 1000x450 canvas in three stage rows. Nodes and edges carry ids
# so the step rail can light them up one at a time.

# id, x, y, w, h, title, sub-lines, icon, kind
PNODES = [
    ("n-gh",     24,  44, 132, 52, "GitHub",          ["public repos"],                              "github", None),
    ("n-lang",  196,  30, 124, 30, "By language",     [],                                            None,     None),
    ("n-stars", 196,  68, 124, 30, "By stars",        [],                                            None,     None),
    ("n-disp",  360,  44, 124, 52, "Dispatcher",      ["route repo"],                                None,     None),
    ("n-repo",  524,  32, 176, 76, "Repository",      ["src/searcher, src/core,", "src/cli, src/regex …"], None, None),

    ("n-base",   24, 176, 150, 54, "Base image",      ["+ repo dependencies"],                       "docker", None),
    ("n-art",   214, 168, 156, 70, "Build scripts",   ["Dockerfile · download.sh", "compile.sh"],    None,     None),
    ("n-exe",   410, 178, 126, 48, "./executable",    [],                                            None,     None),
    ("n-fail",  576, 158, 180, 44, "Build failed",    ["package index unreachable"],                 None,     "bad"),
    ("n-repair",576, 214, 180, 44, "Repair",          ["deps → download.sh"],                        None,     None),
    ("n-valid", 796, 176, 164, 54, "Build validated", ["compile + ldd checks"],                      None,     "good"),

    ("n-sub",    24, 332, 140, 54, "Doc subagents",   ["one per module"],                            None,     None),
    ("n-docs",  194, 332, 140, 54, "Feedback_Docs/",  ["analysis · targets"],                        None,     None),
    ("n-tests", 364, 332, 124, 54, "Test suite",      ["black-box"],                                 None,     None),
    ("n-ana",   518, 320, 156, 78, "Program analysis",["static: CG · DFG · CPG", "dynamic: coverage"],None,     None),
    ("n-chk",   704, 332, 136, 54, "Validation",      ["4 gates"],                                   None,     None),
    ("n-fb",    870, 332, 106, 54, "Feedback",        ["summary"],                                   None,     None),
]

# id, points, label, is-loop
PEDGES = [
    ("e1",  [(156,60),(176,60),(176,45),(196,45)],                None, False),
    ("e2",  [(156,76),(176,76),(176,83),(196,83)],                None, False),
    ("e3",  [(320,45),(340,45),(340,62),(360,62)],                None, False),
    ("e4",  [(320,83),(340,83),(340,78),(360,78)],                None, False),
    ("e5",  [(484,70),(524,70)],                                  None, False),
    ("e6",  [(612,108),(612,132),(99,132),(99,176)],              None, False),
    ("e7",  [(174,203),(214,203)],                                None, False),
    ("e8",  [(370,203),(410,202)],                                None, False),
    ("e9",  [(536,202),(556,202),(556,180),(576,180)],            None, False),
    ("e10", [(666,202),(666,214)],                                None, False),
    ("e11", [(666,258),(666,284),(292,284),(292,240)],            "retry ×1", True),
    ("e12", [(756,236),(776,236),(776,203),(796,203)],            None, False),
    ("e13", [(878,230),(878,300),(94,300),(94,332)],              None, False),
    ("e14", [(164,359),(194,359)],                                None, False),
    ("e15", [(334,359),(364,359)],                                None, False),
    ("e16", [(488,359),(518,359)],                                None, False),
    ("e17", [(674,359),(704,359)],                                None, False),
    ("e18", [(840,359),(870,359)],                                None, False),
    ("e19", [(923,386),(923,424),(426,424),(426,388)],            "iteration ×1", True),
]

PROWS = [(24, 20, "Stage 1 · Repository collection"),
         (24, 152, "Stage 2 · Environment build"),
         (24, 314, "Stage 3 · Black-box test construction")]

# title, node ids, edge ids, body html
PSTEPS = [
    ("Collect repositories", ["n-gh","n-lang","n-stars","n-disp","n-repo"], ["e1","e2","e3","e4","e5"],
     "We crawl public GitHub for real, buildable projects, filtering <b>by language</b> and "
     "<b>by star count</b> so the corpus stays diverse without filling up with toy code. "
     "A dispatcher passes each surviving repository on with its module layout intact."),

    ("Containerise and build", ["n-base","n-art","n-exe"], ["e6","e7","e8"],
     "Each repo gets a base image plus its own dependency setup. The agent writes "
     "<code>Dockerfile</code>, <code>download.sh</code> and <code>compile.sh</code>, then compiles "
     "the project down to a single <code>./executable</code>."),

    ("The build fails", ["n-fail"], ["e9"],
     "First attempts usually don't compile. e.g. the build reaches for a package index that isn't "
     "reachable from inside the sandbox — <code>connection refused</code> — because dependency "
     "fetching was left in the compile step."),

    ("Repair, then rebuild", ["n-repair","n-valid"], ["e10","e11","e12"],
     "The error text goes straight back to the agent, which moves dependency fetching into "
     "<code>download.sh</code> so compilation runs fully offline. Validation re-runs "
     "<code>bash compile.sh</code> and checks <code>ldd ./executable</code>. "
     "<b>One retry is enough</b> — it passes on the second attempt."),

    ("Fan out doc subagents", ["n-sub","n-docs"], ["e13","e14"],
     "A dispatcher splits the repository by module and gives each one its own subagent. Their "
     "findings are validated and collected into <code>Feedback_Docs/</code> — code analysis, "
     "coverage targets, a repair report and a summary."),

    ("Write the test suite", ["n-tests"], ["e15"],
     "Only now are tests written, and only against the compiled binary — no source access. "
     "That restriction is what keeps the resulting benchmark genuinely black-box."),

    ("Analyse and validate", ["n-ana","n-chk"], ["e16","e17"],
     "Static analysis builds the call graph, data-flow graph and code property graph; dynamic "
     "analysis records which functions the suite actually reached. Four gates then screen the "
     "tests: <b>pass</b>, <b>double</b>, <b>dummy</b> and <b>weak-assert</b> checks."),

    ("Feed the result back", ["n-fb"], ["e18"],
     "Every round reports what it moved and what it couldn't. e.g. <i>“search_file() is covered "
     "this iteration; parallel() is unreachable through the black-box executable.”</i>"),

    ("Write the next round", [], ["e19"],
     "That summary seeds the next batch of tests and the loop runs again until coverage stops "
     "moving. <b>One extra iteration</b> is typical — the suite settles on the second pass."),
]


def _round_path(pts, r=8):
    """Orthogonal polyline with softened corners."""
    if len(pts) == 2:
        return f"M{pts[0][0]},{pts[0][1]} L{pts[1][0]},{pts[1][1]}"
    d = [f"M{pts[0][0]},{pts[0][1]}"]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i-1], pts[i], pts[i+1]
        def toward(a, b, rad):
            dx, dy = b[0]-a[0], b[1]-a[1]
            L = math.hypot(dx, dy) or 1
            rad = min(rad, L/2)
            return (b[0]-dx/L*rad, b[1]-dy/L*rad)
        a = toward(p0, p1, r)
        dx, dy = p2[0]-p1[0], p2[1]-p1[1]
        L = math.hypot(dx, dy) or 1
        rr = min(r, L/2)
        c = (p1[0]+dx/L*rr, p1[1]+dy/L*rr)
        d.append(f"L{a[0]:.1f},{a[1]:.1f}")
        d.append(f"Q{p1[0]},{p1[1]} {c[0]:.1f},{c[1]:.1f}")
    d.append(f"L{pts[-1][0]},{pts[-1][1]}")
    return " ".join(d)


def pipe_svg():
    out = []
    for x, y, label in PROWS:
        out.append(f'            <text class="prow" x="{x}" y="{y}">{label}</text>')

    for eid, pts, label, loop in PEDGES:
        cls = "pe loop" if loop else "pe"
        d = _round_path(pts)
        # Arrowhead takes the heading of the final segment.
        (x1, y1), (x2, y2) = pts[-2], pts[-1]
        ang = math.degrees(math.atan2(y2-y1, x2-x1))
        g = [f'            <g class="{cls}" id="{eid}">',
             f'              <path d="{d}"></path>',
             f'              <polygon class="ah" points="0,-3.2 6.4,0 0,3.2" '
             f'transform="translate({x2},{y2}) rotate({ang:.1f})"></polygon>']
        if label:
            # Park the label on the longest run so it never sits on a corner.
            best, blen = None, -1
            for i in range(len(pts)-1):
                L = math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1])
                if L > blen: blen, best = L, i
            mx = (pts[best][0]+pts[best+1][0])/2
            my = (pts[best][1]+pts[best+1][1])/2
            g.append(f'              <text x="{mx:.0f}" y="{my-6:.0f}" text-anchor="middle">{label}</text>')
        g.append('            </g>')
        out.append("\n".join(g))

    for nid, x, y, w, h, title, subs, icon, kind in PNODES:
        cls = "pn" + (f" {kind}" if kind else "")
        tx = x + (32 if icon else 14)
        n = len(subs)
        ty = y + h/2 + (4 if n == 0 else (-3 if n == 1 else -9))
        g = [f'            <g class="{cls}" id="{nid}">',
             f'              <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10"></rect>']
        if icon:
            g.append(f'              <svg class="mi" x="{x+10}" y="{y+h/2-7}" width="14" height="14" '
                     f'viewBox="0 0 24 24"><use href="#ic-{icon}"></use></svg>')
        g.append(f'              <text class="pt" x="{tx}" y="{ty:.0f}">{title}</text>')
        for i, s in enumerate(subs):
            g.append(f'              <text class="ps" x="{tx}" y="{ty + 14 + i*13:.0f}">{s}</text>')
        g.append('            </g>')
        out.append("\n".join(g))
    return "\n".join(out)


def pipe_steps():
    out = []
    for i, (title, _, _, body) in enumerate(PSTEPS):
        out.append(
            f'            <li data-step="{i}">\n'
            f'              <button type="button">\n'
            f'                <span class="sn">STEP {i+1:02d}</span>\n'
            f'                <span class="sh">{title}</span>\n'
            f'                <span class="sb">{body}</span>\n'
            f'              </button>\n'
            f'            </li>')
    return "\n".join(out)

# ── Tables ──────────────────────────────────────────────────────────────────
rows_lang = "\n".join(
    f'            <tr><td>{n}</td><td class="n">{v:,}</td><td class="n">{v/TOTAL*100:.2f}%</td></tr>'
    for n, v, _, _, _ in LANGS)
rows_model = "\n".join(
    f'            <tr><td>{full}</td><td>{"ProgramGym" if o else "Baseline"}</td>'
    f'<td class="n">{s:g}</td></tr>'
    for _, _, full, s, o, _ in MODELS)

# ── Emit ────────────────────────────────────────────────────────────────────
tpl = open(os.path.join(ROOT, 'tools', 'tpl.html'), encoding='utf-8').read()
out = (tpl.replace('{{SPRITE}}', sprite())
          .replace('{{SEGS}}', "\n".join(segs))
          .replace('{{RINGICONS}}', "\n".join(ringicons))
          .replace('{{LEGEND}}', "\n".join(legend))
          .replace('{{BHEAD}}', "\n".join(bhead))
          .replace('{{BARS}}', "\n".join(bars))
          .replace('{{GRID}}', "\n".join(grid))
          .replace('{{ARCS}}', json.dumps([{"from": a, "to": b} for a, b in ARCS]))
          .replace('{{YMAX}}', f"{Y_MAX:g}")
          .replace('{{TOTAL}}', f"{TOTAL:,}")
          .replace('{{TOTALNUM}}', str(TOTAL))
          .replace('{{ROWS_LANG}}', rows_lang)
          .replace('{{ROWS_MODEL}}', rows_model)
          .replace('{{PIPE_SVG}}', pipe_svg())
          .replace('{{PIPE_STEPS}}', pipe_steps())
          .replace('{{PIPE_PLAN}}', json.dumps(
              [{"n": n, "e": e} for _, n, e, _ in PSTEPS])))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print(f"index.html written: {len(out)} bytes")
print(f"donut total {TOTAL} | arcs {ARCS} | bars {len(MODELS)}")
