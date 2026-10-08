# -*- coding: utf-8 -*-
"""Generate index.html. Chart geometry is computed here so the SVG never drifts from the data."""
import math

# ── Data ────────────────────────────────────────────────────────────────────
LANGS = [  # ring order is deliberate: it keeps CVD-weak hue pairs non-adjacent
    ("Go",   818, "var(--c-go)",   "go"),
    ("C++",  378, "var(--c-cpp)",  "cpp"),
    ("Rust", 303, "var(--c-rust)", "rust"),
    ("C",    149, "var(--c-c)",    "c"),
]
TOTAL = sum(v for _, v, _, _ in LANGS)

# (display name, variant, score, is_ours, delta-vs-baseline or None)
MODELS = [
    ("Claude Opus 4.8",  "xhigh",         70.90, False, None),
    ("GPT-5.6 Sol",      "xhigh",         69.90, False, None),
    ("GLM-5.2",          "",              64.60, False, None),
    ("Gemini 3.7",       "Flash",         61.20, False, None),
    ("DS-V4-Flash",      "0731",          57.68, False, None),
    ("Qwen3.8-27B-SFT",  "Program-Agent", 56.25, True,  "+13.4"),
    ("Qwen3.8-27B",      "Program-Agent", 55.71, True,  "+20.8"),
    ("Gemini 3.6",       "Flash",         55.70, False, None),
    ("Kimi K2.7",        "Code",          53.60, False, None),
    ("Qwen3.8-27B-SFT",  "Claude Code",   42.84, True,  None),
    ("Qwen3.8-27B",      "",              34.87, False, None),
]
Y_MAX = 80.0

# ── Donut geometry ──────────────────────────────────────────────────────────
R = 80.0
CIRC = 2 * math.pi * R
GAP = 2.0

segs, legend, cum = [], [], 0.0
for i, (name, val, col, key) in enumerate(LANGS):
    frac = val / TOTAL
    ln = frac * CIRC
    rot = -90 + cum * 360
    delay = round(0.08 + i * 0.13, 3)
    segs.append(
        f'        <circle class="seg" r="{R:g}" cx="130" cy="130"\n'
        f'                stroke="{col}"\n'
        f'                stroke-dasharray="{ln - GAP:.3f} {CIRC - ln + GAP:.3f}"\n'
        f'                style="--len:{ln:.3f}; --d:{delay}s"\n'
        f'                transform="rotate({rot:.4f} 130 130)"\n'
        f'                data-name="{name}" data-count="{val}" data-pct="{frac*100:.2f}"></circle>'
    )
    legend.append(
        f'          <li style="--c:{col}" data-name="{name}">\n'
        f'            <i class="sw"></i>\n'
        f'            <span class="nm">{name}</span>\n'
        f'            <span class="ct">{val:,}</span>\n'
        f'            <span class="pc">{frac*100:.2f}%</span>\n'
        f'          </li>'
    )
    cum += frac

# ── Bars ────────────────────────────────────────────────────────────────────
bars, labs = [], []
for i, (nm, var, score, ours, delta) in enumerate(MODELS):
    h = score / Y_MAX * 100
    delay = round(0.10 + i * 0.055, 3)
    full = f"{nm} ({var})" if var else nm
    cls = "bar ours" if ours else "bar"
    d = f'\n          <span class="bdelta">&uarr; {delta}</span>' if delta else ""
    bars.append(
        f'        <div class="{cls}" style="--h:{h:.3f}%; --d:{delay}s"\n'
        f'             data-name="{full}" data-score="{score:g}"'
        f'{" data-ours=\"1\"" if ours else ""}>\n'
        f'          <span class="bval">{score:g}</span>{d}\n'
        f'          <i class="bfill"></i>\n'
        f'        </div>'
    )
    sub = f"<br>{var}" if var else ""
    lcls = "blab ours" if ours else "blab"
    labs.append(f'        <div class="{lcls}"><b>{nm}</b>{sub}</div>')

gridlines = []
for t in range(0, int(Y_MAX) + 1, 20):
    gridlines.append(
        f'        <div class="gridline" style="bottom:{t / Y_MAX * 100:.2f}%"><span>{t}</span></div>'
    )

# ── Accessible table fallback ───────────────────────────────────────────────
rows_lang = "\n".join(
    f'            <tr><td>{n}</td><td class="n">{v:,}</td><td class="n">{v/TOTAL*100:.2f}%</td></tr>'
    for n, v, _, _ in LANGS)
rows_model = "\n".join(
    f'            <tr><td>{(nm + " (" + var + ")") if var else nm}</td>'
    f'<td>{"ProgramGym" if o else "Baseline"}</td><td class="n">{s:g}</td></tr>'
    for nm, var, s, o, _ in MODELS)

import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
tpl = open(os.path.join(ROOT, 'tools', 'tpl.html'), encoding='utf-8').read()
out = (tpl.replace('{{SEGS}}', "\n".join(segs))
          .replace('{{LEGEND}}', "\n".join(legend))
          .replace('{{BARS}}', "\n".join(bars))
          .replace('{{LABS}}', "\n".join(labs))
          .replace('{{GRID}}', "\n".join(gridlines))
          .replace('{{TOTAL}}', f"{TOTAL:,}")
          .replace('{{ROWS_LANG}}', rows_lang)
          .replace('{{ROWS_MODEL}}', rows_model))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print("index.html written:", len(out), "bytes")
print("donut total:", TOTAL, "| circumference:", round(CIRC, 3))
