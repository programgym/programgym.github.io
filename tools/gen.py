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
          .replace('{{ROWS_MODEL}}', rows_model))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print(f"index.html written: {len(out)} bytes")
print(f"donut total {TOTAL} | arcs {ARCS} | bars {len(MODELS)}")
