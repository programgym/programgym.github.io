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
    ("Opus 4.8",    "xhigh",         "Claude Opus 4.8 (xhigh)",              70.90, False, "claude"),
    ("GPT-5.6",     "xhigh",         "GPT-5.6 Sol (xhigh)",                  69.90, False, "openai"),
    ("GLM-5.2",     "",              "GLM-5.2",                              64.60, False, "zai"),
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

# Jump curves, as Figure 1 draws them: (source, target, dashed, scale).
# Solid = the Program-Env gain, dashed = the Program-Agent gain. Each lands on
# an "ours" bar. `scale` shrinks the lift of arcs that span the same number of
# columns so they nest instead of landing on top of each other.
ARCS = [
    (10, 6, True,  1.00),   # Qwen3.8-27B            -> + Program-Agent
    (9,  5, True,  0.58),   # Qwen3.8-27B-SFT + CC   -> + Program-Agent
    (10, 9, False, 0.95),   # Qwen3.8-27B            -> SFT, trained in Program-Env
]

ICON_CLASS = {
    "claude": "i-claude", "openai": "i-openai", "zai": "i-zai",
    "google": "i-google", "deepseek": "i-deepseek", "qwen": "i-qwen",
    "kimi": "i-kimi", "go": "i-go", "cplusplus": "i-cpp", "rust": "i-rust", "c": "i-c",
}

# ── Icon sprite ─────────────────────────────────────────────────────────────
def sprite():
    """Fold the vendored SVGs into one inline <symbol> sprite.

    Two kinds of file live in tools/icons/:

      * monochrome (simple-icons, and devicon's rust) — no fill anywhere, so
        the shapes inherit `fill: currentColor` from .mi and the .i-* colour
        tokens tint them, which is what makes dark mode work;
      * full-colour (devicon) — every shape carries its own fill. Those are
        wrapped in <g fill="#000"> so the few shapes that rely on SVG's black
        default (the gopher's outlines) keep it instead of inheriting
        currentColor and coming out cyan.

    Everything between the root <svg> and </svg> is kept, so <defs> and
    <clipPath> survive; xlink:href is rewritten to plain href for inline HTML.
    """
    out, seen_ids = [], {}
    for name in sorted(os.listdir(os.path.join(ROOT, 'tools', 'icons'))):
        if not name.endswith('.svg'):
            continue
        key = name[:-4]
        raw = open(os.path.join(ROOT, 'tools', 'icons', name), encoding='utf-8').read()
        raw = re.sub(r'<\?xml.*?\?>|<!DOCTYPE.*?>|<!--.*?-->', '', raw, flags=re.S)
        head = re.search(r'<svg\b[^>]*>', raw)
        vb = re.search(r'viewBox="([^"]+)"', head.group(0)).group(1)
        body = raw[head.end():raw.rindex('</svg>')]
        body = re.sub(r'<title>.*?</title>', '', body, flags=re.S)
        body = body.replace('xlink:href=', 'href=')
        body = re.sub(r'\s+', ' ', body).strip()

        # ids leak into the page's global namespace once inlined.
        for i in re.findall(r'\bid="([^"]+)"', body):
            assert i not in seen_ids, f'duplicate id {i!r} in {name} and {seen_ids[i]}'
            seen_ids[i] = name

        if 'fill="' in body:
            body = f'<g fill="#000">{body}</g>'
        out.append(f'  <symbol id="ic-{key}" viewBox="{vb}">{body}</symbol>')
    return '\n'.join(out)

def icon_svg(key, cls_extra=""):
    return (f'<svg class="mi" aria-hidden="true"><use href="#ic-{key}"></use></svg>')

# ── Donut ───────────────────────────────────────────────────────────────────
R, CIRC, GAP = 80.0, 2 * math.pi * 80.0, 2.0
CX = CY = 130.0

segs, legend, cum = [], [], 0.0
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
    legend.append(
        f'            <li class="reveal" style="--c:{col};--i:{i + 1}" data-name="{name}">\n'
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
    ours_attr = ' data-ours="1"' if ours else ''
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
        f'{ours_attr}>\n'
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
import hashlib
# Cache-buster for the embedded walkthrough: changes exactly when program-env.html changes,
# so a deploy never leaves the browser holding a stale 1.5 MB iframe (Pages caches for 10 min).
def _hash(*parts):
    p = os.path.join(ROOT, *parts)
    return hashlib.md5(open(p, 'rb').read()).hexdigest()[:10] if os.path.exists(p) else '0'

PEV = _hash('program-env.html')
PAV = _hash('program-agent.html')   # the agent walkthrough iframe, same reason
# index.html and main.css are fetched separately and Pages serves both with
# max-age=600, so without this a deploy can leave a browser pairing the new
# markup with the stylesheet it already had — new class names matching no rule.
# Re-run gen.py after editing main.css, or the page keeps the stale query.
CSSV = _hash('static', 'css', 'main.css')
TIPV = _hash('static', 'js', 'tooltips.js')
tpl = open(os.path.join(ROOT, 'tools', 'tpl.html'), encoding='utf-8').read()
out = (tpl.replace('{{PEV}}', PEV)
          .replace('{{PAV}}', PAV)
          .replace('{{CSSV}}', CSSV)
          .replace('{{TIPV}}', TIPV)
          .replace('{{SPRITE}}', sprite())
          .replace('{{SEGS}}', "\n".join(segs))
          .replace('{{LEGEND}}', "\n".join(legend))
          .replace('{{BHEAD}}', "\n".join(bhead))
          .replace('{{BARS}}', "\n".join(bars))
          .replace('{{GRID}}', "\n".join(grid))
          .replace('{{ARCS}}', "[\n" + ",\n".join(
              f'    {{ from: {a}, to: {b}, dashed: {"true" if d else "false"}, scale: {sc:.2f} }}'
              for a, b, d, sc in ARCS) + "\n  ]")
          .replace('{{YMAX}}', f"{Y_MAX:g}")
          .replace('{{TOTAL}}', f"{TOTAL:,}")
          .replace('{{TOTALNUM}}', str(TOTAL))
          .replace('{{ROWS_LANG}}', rows_lang)
          .replace('{{ROWS_MODEL}}', rows_model))
open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(out)
print(f"index.html written: {len(out)} bytes")
print(f"donut total {TOTAL} | arcs {len(ARCS)} | bars {len(MODELS)} | css v{CSSV}")
